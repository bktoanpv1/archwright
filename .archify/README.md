# Sơ đồ kiến trúc theo domain (.archify)

Mỗi domain pack của archwright là một thư mục `domains/<tên-domain-pack>/`, trong đó có một **gói sơ đồ** tự chứa. Thư mục `.archify/` này chỉ chứa công cụ build và mục lục. Mọi gói dùng cùng 4 khối ([docs/architecture.md §1](../docs/architecture.md#1-ý-tưởng-cốt-lõi)) và cùng bộ sơ đồ chuẩn; chỉ nội dung thay đổi theo domain.

## Domain

| Domain | Mô tả | Sơ đồ |
| --- | --- | --- |
| [embedded-mcu](../domains/embedded-mcu/README.md) | Lập trình nhúng / IoT: thiết kế mạch + firmware | 01 tổng quan · 02 vòng lặp tính năng |
| [llm-agent](../domains/llm-agent/README.md) | Sản phẩm xây trên LLM: agent có công cụ, hội thoại | 01 tổng quan · 02 vòng lặp thay đổi · 03 vòng đời phiên bản · 04 vòng dữ liệu eval |
| [pcb-design](../domains/pcb-design/README.md) | Thiết kế mạch in: schematic, layout, sản xuất, bring-up | 01 tổng quan · 02 vòng lặp một rev board · 03 vòng đời rev · 04 chuỗi dẫn xuất |
| [mechanical-design](../domains/mechanical-design/README.md) | Thiết kế cơ khí (MCAD), hiện tập trung vào vỏ: CAD, mẫu in 3D, khuôn ép | 01 tổng quan · 02 vòng lặp một mẫu vỏ |

## Cấu trúc

```text
archwright/
├── .archify/
│   ├── README.md              # mục lục domain (file này)
│   ├── build.py               # build mọi gói: domains/<domain>/src/ -> dist/
│   └── .gitignore             # bỏ qua .receipts/
├── domains/
│   ├── _template/             # mẫu để tạo domain mới
│   │   └── README.md
│   └── embedded-mcu/          # một domain pack
│       ├── README.md          # bản kê của domain: sơ đồ + nội dung 4 khối
│       ├── research.md        # (tuỳ chọn) ghi chép nghiên cứu
│       ├── src/               # NGUỒN sơ đồ, sửa ở đây
│       ├── dist/              # HTML sinh tự động, không sửa tay
│       └── .receipts/         # biên nhận kiểm tra (git bỏ qua)
└── repositories/              # repo tham khảo (git bỏ qua)
```

## Quy ước

- Tên thư mục domain trùng tên domain pack, ví dụ `domains/embedded-mcu/`. Tên domain pack đặt theo đặc điểm làm domain khác biệt (cách kiểm chứng, nguồn tri thức), không theo tên một dự án cụ thể.
- Bộ sơ đồ chuẩn của mọi gói: `01-overview.architecture.json` (4 khối) và `02-feature-loop.workflow.json` (vòng lặp). Sơ đồ riêng của domain đánh số từ `03`.
- Tên file nguồn: `<NN>-<tên>.<loại>.json`, trong đó `<loại>` trùng với `diagram_type` trong file.
- `meta.output` trong file nguồn phải là `domains/<domain>/dist/<NN>-<tên>.html` (build.py kiểm tra).
- build.py coi mọi thư mục trong `domains/` có `src/*.<loại>.json` là một gói; thư mục bắt đầu bằng `_` hoặc `.` không được build.

## Thêm domain mới

1. `cp -r domains/_template domains/<ten-domain>` rồi `mkdir domains/<ten-domain>/src` (chạy ở gốc repo).
2. Copy hai sơ đồ chuẩn từ `domains/embedded-mcu/src/` làm điểm xuất phát, sửa nội dung và `meta.output`.
3. Điền README của domain, thêm một dòng vào bảng Domain ở trên.
4. `python .archify/build.py <ten-domain>`.

## Build

Yêu cầu: Python ≥ 3.9, Node.js và skill archify tại `~/.agents/skills/archify/bin/archify.mjs` (hoặc đặt biến `ARCHIFY_BIN`).

```bash
python .archify/build.py                    # mọi domain
python .archify/build.py embedded-mcu       # một domain
python .archify/build.py embedded-mcu 02    # một sơ đồ
```

`PASS` nghĩa là đã qua các bước validate, deliver, check và browser-check tự động; chưa phải là đã xem bằng mắt.
