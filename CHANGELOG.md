# Changelog

## v0.1.0 (2026-10-30)

Bản phát hành đầu tiên, ở giai đoạn thiết kế.

- Tài liệu thiết kế: kiến trúc ([docs/architecture.md](docs/architecture.md)) và mô hình khái quát của core v0.2 ([docs/core-model.md](docs/core-model.md)).
- Nghiên cứu chuẩn tài liệu, đặc tả ba form `approval`, `baseline`, `deviation` và bốn bản thử giấy.
- `doclint`: công cụ đầu tiên của core, kiểm frontmatter, mục bắt buộc, liên kết, anchor, con số có nguồn và luật chéo giữa tài liệu; 30 test.
- Thư mục `domains/` với bốn domain `embedded-mcu`, `llm-agent`, `pcb-design`, `mechanical-design`: 12 sơ đồ archify, ghi chép nghiên cứu cho `llm-agent` và `pcb-design`, cùng `build.py` và mẫu tạo domain mới.
