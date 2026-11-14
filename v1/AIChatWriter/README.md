# AI Chat cho LibreOffice Writer – v0.1.0 (Giai đoạn 1 + 2)

## Giai đoạn 1 – Quyết định kiến trúc (đã kiểm chứng trên LibreOffice 24.2)

| Vấn đề | Kết luận | Lý do |
|---|---|---|
| Vị trí khung chat | **Sidebar Deck + Panel** (Sidebar.xcu + Factories.xcu) | Nằm ở cạnh phải, đóng/mở bằng tab có sẵn, không che vùng soạn thảo, mỗi cửa sổ Writer có panel riêng |
| Ngôn ngữ | **Python-UNO** | LibreOffice trên Windows có sẵn Python; không cần biên dịch như C++/Java, không cần cài JRE |
| Giao diện HTML/JS | **Không dùng** | Bộ điều khiển giao diện (AWT) của LibreOffice không có điều khiển trình duyệt web nào nhúng được (đã kiểm tra danh sách dịch vụ). Giao diện dựng bằng control gốc: nút, ô văn bản nhiều dòng |
| Hiển thị Markdown | Chuyển Markdown sang văn bản thuần dễ đọc trong ô lịch sử (GĐ 3); khi **chèn vào tài liệu** thì áp định dạng Writer thật (đậm, nghiêng, tiêu đề, khối code) qua UNO (GĐ 6) | Ô văn bản AWT không hiển thị được định dạng phong phú |
| Gọi API | `urllib.request` của thư viện chuẩn, chạy ở **luồng nền** | Không phụ thuộc pip; không làm treo Writer |
| Cập nhật giao diện từ luồng nền | `com.sun.star.awt.AsyncCallback` | Gọi UNO trực tiếp từ luồng khác có thể gây treo hoặc lỗi |
| Lưu API key | `com.sun.star.task.PasswordContainer` (kho mật khẩu của LibreOffice, có thể khóa bằng mật khẩu chính) | Không ghi key vào mã nguồn hay file cấu hình thô |
| Cấu hình khác | Kho cấu hình riêng (registry .xcs/.xcu) của extension | Chuẩn LibreOffice, theo từng hồ sơ người dùng |

## Cấu trúc

```
description.xml            thông tin extension (id: vn.aichat.writer)
META-INF/manifest.xml      khai báo component Python + file cấu hình
registry/Sidebar.xcu       Deck "AI Chat" + Panel, chỉ hiện trong Writer
registry/Factories.xcu     ánh xạ URL panel -> factory Python
python/aichat_component.py PanelFactory + ChatPanel (UNO)
python/pythonpath/aichat/  module dùng chung (tự vào sys.path)
dialogs/ChatPanel.xdl      khai báo các control của panel
icons/chat.png             biểu tượng tab Sidebar
```

## Cài đặt / gỡ

- Giao diện: Công cụ ▸ Trình quản lý phần mở rộng ▸ Thêm ▸ chọn `AIChatWriter.oxt`, rồi khởi động lại LibreOffice.
- Dòng lệnh (Windows): `"C:\Program Files\LibreOffice\program\unopkg.com" add AIChatWriter.oxt`
- Mở: bấm biểu tượng bong bóng chat ở thanh Sidebar bên phải (hoặc Xem ▸ Sidebar).
- Log lỗi: `%TEMP%\aichat_writer.log`

## Trạng thái hiện tại

Khung hoạt động: panel hiển thị, co giãn theo Sidebar, các nút Chat mới, Cài đặt và Gửi đều nhận sự kiện.
Nút Gửi tạm thời chỉ lặp lại (echo) tin nhắn; **chưa gọi AI và chưa đọc hay ghi tài liệu**.

## Các giai đoạn tiếp theo

3. Hoàn thiện giao diện: trạng thái Loading, chuyển Markdown sang văn bản, Enter để gửi, nút Copy/Chèn/Thay thế
4. `ai_client.py`: gửi/nhận qua REST (OpenAI-compatible, Anthropic, Gemini), luồng nền, timeout, xử lý lỗi
5. `document.py`: đọc vùng chọn, các lệnh nhanh (Tóm tắt, Kiểm tra chính tả, Viết lại, Dịch, Giải thích)
6. Chèn tại con trỏ / thay vùng chọn (có hộp xác nhận, gom một bước Hoàn tác)
7. Hộp thoại Cài đặt + PasswordContainer
8. Kiểm thử trên Windows, đóng gói
