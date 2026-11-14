"""Tính bố cục panel theo pixel để khung chat co giãn theo chiều rộng/cao của Sidebar."""

POSSIZE = 15  # com.sun.star.awt.PosSize.POSSIZE

PAD = 6
BTN_H = 26
STATUS_H = 18
INPUT_H = 80
MIN_HISTORY_H = 120


def layout(container, width, height):
    """Đặt lại vị trí các control bên trong `container` (XControlContainer)."""
    w = max(width - 2 * PAD, 80)
    y = PAD

    half = (w - PAD) // 2
    container.getControl("btnNewChat").setPosSize(PAD, y, half, BTN_H, POSSIZE)
    container.getControl("btnSettings").setPosSize(PAD + half + PAD, y, half, BTN_H, POSSIZE)
    y += BTN_H + PAD

    bottom_block = STATUS_H + PAD + INPUT_H + PAD + BTN_H + PAD
    history_h = max(height - y - bottom_block, MIN_HISTORY_H)
    container.getControl("txtHistory").setPosSize(PAD, y, w, history_h, POSSIZE)
    y += history_h + PAD

    container.getControl("lblStatus").setPosSize(PAD, y, w, STATUS_H, POSSIZE)
    y += STATUS_H + PAD

    container.getControl("txtInput").setPosSize(PAD, y, w, INPUT_H, POSSIZE)
    y += INPUT_H + PAD

    send_w = min(110, w)
    container.getControl("btnSend").setPosSize(PAD + w - send_w, y, send_w, BTN_H, POSSIZE)
    y += BTN_H + PAD
    return y  # tổng chiều cao tối thiểu cần dùng
