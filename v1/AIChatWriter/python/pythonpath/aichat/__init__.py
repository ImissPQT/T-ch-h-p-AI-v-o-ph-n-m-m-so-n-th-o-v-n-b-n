"""Thư viện nội bộ của extension AI Chat cho Writer.

Thư mục `pythonpath/` cạnh file component được LibreOffice tự thêm vào sys.path,
nên các module ở đây import được bằng `from aichat import ...`.
Các giai đoạn sau sẽ thêm: ai_client.py (REST), document.py (UNO Writer),
settings.py (cấu hình + PasswordContainer), render.py (Markdown -> văn bản).
"""
EXTENSION_ID = "vn.aichat.writer"
