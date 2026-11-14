# -*- coding: utf-8 -*-
"""Component UNO: factory tạo AI Chat Panel trong Sidebar của LibreOffice Writer.

Luồng hoạt động:
  Sidebar.xcu  -> ImplementationURL private:resource/toolpanel/AIChatPanelFactory/AIChatPanel
  Factories.xcu -> ánh xạ "AIChatPanelFactory" tới implementation vn.aichat.writer.PanelFactory
  PanelFactory.createUIElement() -> ChatPanel (XUIElement + XToolPanel + XSidebarPanel)

Giai đoạn 2: chỉ là khung. Nút Gửi tạm thời "echo" lại tin nhắn để kiểm chứng
giao diện và sự kiện; giai đoạn 4 sẽ thay bằng lời gọi AI chạy ở luồng nền.
"""
import os
import sys
import tempfile
import traceback

import uno
import unohelper
from com.sun.star.awt import XActionListener, XWindowListener
from com.sun.star.lang import XComponent
from com.sun.star.ui import XUIElement, XToolPanel, XSidebarPanel, XUIElementFactory, LayoutSize

from aichat import EXTENSION_ID
from aichat.layout import layout

IMPL_NAME = "vn.aichat.writer.PanelFactory"
LOG_PATH = os.path.join(tempfile.gettempdir(), "aichat_writer.log")


def log(msg):
    """Ghi log ra %TEMP%/aichat_writer.log (Windows) để dễ chẩn đoán lỗi."""
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(msg.rstrip() + "\n")
    except Exception:
        pass


def extension_url(ctx, relative):
    pip = ctx.getValueByName("/singletons/com.sun.star.deployment.PackageInformationProvider")
    return pip.getPackageLocation(EXTENSION_ID) + "/" + relative


class _ButtonListener(unohelper.Base, XActionListener):
    def __init__(self, callback):
        self._cb = callback

    def actionPerformed(self, ev):
        try:
            self._cb()
        except Exception:
            log(traceback.format_exc())

    def disposing(self, ev):
        pass


class _ResizeListener(unohelper.Base, XWindowListener):
    def __init__(self, panel):
        self._panel = panel

    def windowResized(self, ev):
        self._panel.relayout()

    def windowMoved(self, ev): pass
    def windowShown(self, ev): pass
    def windowHidden(self, ev): pass
    def disposing(self, ev): pass


class ChatPanel(unohelper.Base, XUIElement, XToolPanel, XSidebarPanel, XComponent):
    """Một panel cho mỗi cửa sổ Writer (mỗi Frame có một Sidebar riêng)."""

    def __init__(self, ctx, frame, parent_window, resource_url):
        self.ctx = ctx
        self.Frame = frame
        self.ResourceURL = resource_url
        self.Type = uno.getConstantByName("com.sun.star.ui.UIElementType.TOOLPANEL")
        self.parent = parent_window
        self.history = []  # [(role, text)] - giai đoạn 4 dùng làm ngữ cảnh hội thoại

        provider = ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.awt.ContainerWindowProvider", ctx)
        self.Window = provider.createContainerWindow(
            extension_url(ctx, "dialogs/ChatPanel.xdl"), "", parent_window, None)
        self.Window.setVisible(True)

        self._listeners = []
        self._bind("btnSend", self.on_send)
        self._bind("btnNewChat", self.on_new_chat)
        self._bind("btnSettings", self.on_settings)

        self._resize = _ResizeListener(self)
        parent_window.addWindowListener(self._resize)
        self.set_status("Sẵn sàng (khung giai đoạn 2 – chưa kết nối AI)")
        self.relayout()

    # ---------- tiện ích ----------
    def ctl(self, name):
        return self.Window.getControl(name)

    def _bind(self, name, cb):
        lst = _ButtonListener(cb)
        self._listeners.append(lst)
        self.ctl(name).addActionListener(lst)

    def set_status(self, text):
        self.ctl("lblStatus").getModel().Label = text

    def relayout(self):
        size = self.parent.getPosSize()
        self.Window.setPosSize(0, 0, size.Width, size.Height, 15)
        layout(self.Window, size.Width, size.Height)

    def render_history(self):
        lines = []
        for role, text in self.history:
            who = "Bạn" if role == "user" else "AI"
            lines.append("%s:\n%s\n" % (who, text))
        edit = self.ctl("txtHistory")
        edit.getModel().Text = "\n".join(lines)
        n = len(edit.getModel().Text)
        edit.setSelection(uno.createUnoStruct("com.sun.star.awt.Selection", n, n))  # cuộn xuống cuối

    # ---------- sự kiện ----------
    def on_send(self):
        model = self.ctl("txtInput").getModel()
        text = model.Text.strip()
        if not text:
            return
        model.Text = ""
        self.history.append(("user", text))
        self.history.append(("assistant", "(echo – giai đoạn 4 sẽ gọi AI) " + text))
        self.render_history()

    def on_new_chat(self):
        self.history = []
        self.render_history()
        self.set_status("Đã tạo cuộc hội thoại mới")

    def on_settings(self):
        self.set_status("Cài đặt sẽ được xây dựng ở giai đoạn 7")

    # ---------- XUIElement ----------
    def getRealInterface(self):
        return self

    # ---------- XToolPanel ----------
    def createAccessible(self, parent_accessible):
        return self.Window

    # ---------- XSidebarPanel ----------
    def getHeightForWidth(self, width):
        # Tối thiểu 300px, không giới hạn tối đa (-1) => panel giãn hết chiều cao Deck
        return LayoutSize(300, -1, 400)

    def getMinimalWidth(self):
        # Nhỏ hơn bề rộng Sidebar mặc định để không phát sinh thanh cuộn ngang
        return 160

    # ---------- XComponent ----------
    def dispose(self):
        try:
            self.parent.removeWindowListener(self._resize)
            self.Window.dispose()
        except Exception:
            log(traceback.format_exc())

    def addEventListener(self, l): pass
    def removeEventListener(self, l): pass


class PanelFactory(unohelper.Base, XUIElementFactory):
    def __init__(self, ctx):
        self.ctx = ctx

    def createUIElement(self, url, args):
        try:
            props = {a.Name: a.Value for a in args}
            parent = props.get("ParentWindow")
            if parent is None:
                raise RuntimeError("Thiếu ParentWindow")
            if url.endswith("/AIChatPanel"):
                return ChatPanel(self.ctx, props.get("Frame"), parent, url)
            raise RuntimeError("Không hỗ trợ: " + url)
        except Exception:
            log(traceback.format_exc())
            raise


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(
    PanelFactory, IMPL_NAME, ("com.sun.star.ui.UIElementFactory",))
