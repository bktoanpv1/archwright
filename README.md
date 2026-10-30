# archwright

> Architect every project right from day one.

archwright là bộ khung khởi tạo dự án, giúp một dự án mới đi đúng hướng ngay từ ngày đầu. Mỗi dự án sinh ra đã có sẵn ba thứ: tri thức đã chưng cất từ tài liệu của lĩnh vực, các agent đã được chuẩn hoá vai trò, và một vòng kiểm chứng cho biết thay đổi nào là đúng.

archwright chuẩn hoá chức năng chứ không chuẩn hoá nội dung. Phần dùng chung cho mọi lĩnh vực được giữ gọn và ổn định. Phần riêng của từng lĩnh vực nằm trong một domain pack, nên muốn chuyển sang lĩnh vực khác chỉ cần thay domain pack. Bài học đã kiểm chứng ở từng dự án được đưa ngược lại domain pack, nhờ đó các dự án sau khởi đầu tốt hơn.

Nguyên tắc bao trùm: người giữ quyền phán quyết và chịu trách nhiệm, AI gánh khối lượng. Vòng kiểm chứng quyết định AI được tự làm tới đâu.

## Trạng thái

Dự án đang ở giai đoạn thiết kế. Bản này gồm tài liệu thiết kế, sơ đồ của bốn domain và công cụ đầu tiên của core (`doclint`). Trình sinh dự án (`kit/new_project.py`), phần `domain.toml` và `overlay/` của domain pack, và dự án demo mô tả trong [docs/architecture.md](docs/architecture.md) chưa có.

## Nội dung

| Đường dẫn | Nội dung |
| --- | --- |
| [docs/architecture.md](docs/architecture.md) | Kiến trúc: 5 chức năng, ba tầng core / domain pack / dự án, agent, vòng đời tri thức |
| [docs/core-model.md](docs/core-model.md) | Mô hình khái quát của core: 7 khái niệm để mô tả mọi dự án |
| [docs/research/](docs/research/) | Nghiên cứu chuẩn tài liệu và đặc tả các form (approval, baseline, deviation) |
| [docs/paper-tests/](docs/paper-tests/) | Thử giấy: đặt từng domain vào đề xuất để tìm lỗ hổng |
| [kit/core/tools/doclint.py](kit/core/tools/doclint.py) | Kiểm hình thức tài liệu theo `type` / `form`, trả PASS / FAIL / BLOCKED |
| [domains/](.archify/README.md#domain) | Domain pack, mỗi lĩnh vực một thư mục: [embedded-mcu](domains/embedded-mcu/README.md), [llm-agent](domains/llm-agent/README.md), [pcb-design](domains/pcb-design/README.md), [mechanical-design](domains/mechanical-design/README.md). Hiện mỗi domain có sơ đồ; `llm-agent` và `pcb-design` có thêm ghi chép nghiên cứu |
| [.archify/](.archify/README.md) | Công cụ build sơ đồ và mục lục domain |

Sơ đồ ở `domains/<domain>/dist/*.html` là HTML tự chứa, mở trực tiếp bằng trình duyệt.

## Chạy

Yêu cầu: Python ≥ 3.11 (`doclint` dùng `tomllib`). Build sơ đồ cần thêm Node.js và skill archify, xem [.archify/README.md](.archify/README.md#build).

```bash
python kit/core/tools/doclint.py docs/ --config doclint.toml   # kiểm tài liệu của repo
python kit/core/tools/test_doclint.py                          # test của doclint
python .archify/build.py                                       # build lại mọi sơ đồ
```

## Repo tham khảo

Thiết kế dựa trên ý tưởng từ các repo sau (clone vào `repositories/` để đọc, thư mục này không được commit):

- [book-to-skill](https://github.com/toanpv-tech/book-to-skill): chưng cất sách thành skill, đường *distill* ở [architecture.md §3](docs/architecture.md#3-tri-thức-hai-đường-xử-lý).
- [ponytail](https://github.com/DietrichGebert/ponytail): kỷ luật viết code cho agent `builder`.

## Giấy phép

Mã nguồn và tài liệu của archwright phát hành theo [MIT](LICENSE).

- Tên công cụ, sản phẩm và tiêu chuẩn nhắc tới trong tài liệu (ví dụ ISO/IEC/IEEE, MISRA C, AUTOSAR, UL, KiCad, FreeCAD) thuộc chủ sở hữu tương ứng và chỉ dùng để tham chiếu. Giấy phép MIT không áp lên chúng, và việc nhắc tên không cấp quyền dùng chúng.
- Repo không chép nội dung của tiêu chuẩn có bản quyền, chỉ ghi tên chuẩn, mã điều khoản và diễn giải do nhóm tự viết ([doc-standards.md](docs/research/doc-standards.md)).
- File `domains/<domain>/dist/*.html` do [archify](https://github.com/tt-a1i/archify) sinh ra, có nhúng runtime và font của bên thứ ba; giấy phép của chúng (Apache-2.0, SIL OFL 1.1) đã nằm sẵn trong từng file.
