# Domain: PCB Design System

Gói sơ đồ của domain pack `pcb-design`: thiết kế mạch in, từ kiến trúc khối và chọn linh kiện tới schematic, layout, gửi sản xuất và bring-up board thật. Quy ước và cách build: [.archify/README.md](../../.archify/README.md). Mô hình khái quát dùng chung: [docs/core-model.md](../../docs/core-model.md). Căn cứ và nguồn của mọi khẳng định dưới đây: [research.md](research.md).

## Sơ đồ

| # | Sơ đồ | Loại | Nguồn | Xem |
| --- | --- | --- | --- | --- |
| 01 | Tổng quan 4 khối, thêm phần sản xuất (nhà máy, kết quả bring-up) | architecture | [src](src/01-overview.architecture.json) | [dist](dist/01-overview.html) |
| 02 | Vòng lặp một rev board: kiến trúc → duyệt → schematic → ERC/BOM lần 1 → chốt schematic → placement → duyệt placement → routing → DRC/parity → review → gói sản xuất/BOM lần 2 → chốt gửi sản xuất → sản xuất + bring-up → errata | workflow | [src](src/02-feature-loop.workflow.json) | [dist](dist/02-feature-loop.html) |
| 03 | Vòng đời một rev: mở → schematic chốt → chốt gửi sản xuất → sản xuất → bring-up → đạt; các trạng thái chờ người (linh kiện, EQ), rework, rev mới | lifecycle | [src](src/03-board-rev.lifecycle.json) | [dist](dist/03-board-rev.html) |
| 04 | Chuỗi dẫn xuất artefact: nguồn đã kiểm → thiết kế sửa tay → file sinh ra → manifest rev → nhà máy và các domain khác | dataflow | [src](src/04-derivation.dataflow.json) | [dist](dist/04-derivation.html) |

## 4 khối của domain

| Khối | Nội dung trong domain này |
| --- | --- |
| **1 · Tri thức** | Datasheet, luật DFM và năng lực nhà máy (chỉ trích xuất, tra kèm số trang) · App note, thiết kế mẫu, checklist review schematic/layout của hãng chip, kinh nghiệm SI/PI, EMC, layout (chưng cất) · Tiêu chuẩn IPC-7351, IPC-2221, IPC-2152, IPC-6012, IPC-A-610, RoHS/REACH (chỉ mã điều khoản) · Tri thức nội bộ: decisions, errata theo rev, nhật ký bring-up theo serial, thư viện symbol/footprint đã kiểm · Tồn kho, giá, vòng đời linh kiện: tra API lúc dùng, ghi kèm ngày |
| **2 · Agent & công cụ** | lớp sửa có cấu trúc, chưa chốt: thiết kế dạng code (SKiDL, atopile) sinh netlist hoặc schematic, hoặc thư viện đọc ghi S-expression; placement và routing vẫn làm trong KiCad · `kicad-cli`: ERC, DRC (JSON, exit code, `--schematic-parity`), xuất gói sản xuất bằng jobset · bộ sinh footprint IPC-7351 · tính toán: ngspice chạy riêng, IPC-2152, trở kháng · kiểm BOM qua API phân phối (DigiKey, Mouser, jlcparts) · diff trực quan giữa hai rev (KiRI) · bench bring-up |
| **3 · Workflow** | planner (khối, power tree, linh kiện chính) → duyệt kiến trúc → builder schematic + BOM + pin map → ERC, BOM lần 1 → chốt schematic → builder stackup + placement → duyệt placement → builder routing → DRC, parity → reviewer → gói sản xuất, BOM lần 2 → chốt gửi sản xuất → sản xuất + bring-up → verifier (checklist theo serial) → curator (errata, rework, ECO) |
| **4 · Mô hình hoá domain** | Kiểm chứng thật rất chậm và tốn tiền nên mọi kiểm tra rẻ dồn về trước khi đặt hàng · Ba lần thực hiện nối tiếp (schematic, placement, routing), mỗi lần có cổng riêng · Không rollback, chỉ rework hoặc rev mới · Rev và serial board là khoá của bằng chứng · Đầu ra sinh ra không được cũ hơn nguồn · Pin map, power tree chung với `embedded-mcu`; biên board chung với `mechanical-design` |

## Các bước

Mô tả bằng thuộc tính bước của [core-model §3](../../docs/core-model.md#3-bước-một-khái-niệm-thay-cho-mọi-slot). Tốc độ và chi phí là ước lượng định tính, không phải số đo.

| Bước | Loại | Vai trò | Tốc độ · chi phí | Bằng chứng | Khi không chạy được |
| --- | --- | --- | --- | --- | --- |
| Kiến trúc, power tree, chọn linh kiện chính | `design` | planner | giờ | phán đoán; mọi số có trích trang | |
| Duyệt kiến trúc | `decide` | người | | phán đoán | |
| Tính toán (SPICE, IPC-2152, nguồn) | `check` | công cụ | phút | chỉ số theo ngưỡng | BLOCKED |
| Schematic, BOM, pin map | `make` | builder | giờ | | |
| ERC | `check` | `kicad-cli sch erc --exit-code-violations` | giây | nhị phân (exit 0/5) + JSON | BLOCKED |
| BOM lần 1: vòng đời, số nguồn, linh kiện thay thế | `check` | công cụ + API | phút, theo hạn mức API | chỉ số, ghi kèm ngày | BLOCKED, người quyết |
| Chốt schematic | `decide` | người | | phán đoán theo checklist; baseline 1 | |
| Stackup, placement | `make` | builder | giờ | | |
| Duyệt placement | `decide` | người (cùng kỹ sư cơ khí khi đổi biên) | | phán đoán | |
| Routing, đổ đồng | `make` | builder hoặc bộ route chuyên dụng | giờ–ngày | | |
| DRC + parity | `check` | `kicad-cli pcb drc --schematic-parity` với `.kicad_dru` của nhà máy | giây | nhị phân + JSON | BLOCKED |
| Review layout | `check` | reviewer | | phán đoán theo checklist, kèm diff rev | |
| Gói sản xuất, BOM lần 2 | `check` | jobset + API | phút | nhị phân (manifest khớp nguồn) + chỉ số (tồn kho, giá) | BLOCKED, người quyết |
| Chốt gửi sản xuất | `decide` | người | | phán đoán; baseline 2 | |
| Sản xuất, trả lời EQ | `release` | nhà máy; người trả lời EQ | tuần, tiền thật | | chờ |
| Bring-up | `check` | verifier + người ở bench | ngày, bench | chỉ số theo checklist, theo serial | BLOCKED |
| Errata, rework, ECO | `learn` | curator | | | |

Điều kiện kích hoạt (`when`) đáng ghi: chỉ chạy lại tính toán nguồn khi đổi khối nguồn; đổi biên board hoặc lỗ vít thì duyệt placement cần người của `mechanical-design`; đổi pin map thì cần người của `embedded-mcu`.

## Quy tắc cho agent

Rút từ bằng chứng ở [research.md §3](research.md#3-ai-trong-thiết-kế-pcb-làm-được-gì-hỏng-ở-đâu). Đây là nội dung đề xuất cho `checklists/review.md` của pack.

1. Pinout, kích thước footprint, định mức không bao giờ lấy từ trí nhớ của model hay bản tóm tắt. Đọc bảng trong datasheet của hãng, ghi bản datasheet, trang và bảng cho từng giá trị.
2. Không tự vẽ footprint. Sinh bằng bộ sinh IPC-7351; agent chỉ điền bảng kích thước có trích trang, người đối chiếu bản vẽ package trước khi đặt hàng.
3. Chỉ chọn linh kiện qua API phân phối hoặc catalog đang sống. MPN không tra được thì coi như bịa.
4. Sửa thiết kế qua lớp có cấu trúc (thư viện đọc ghi S-expression, hoặc thiết kế dạng code) chứ không sửa tay văn bản `.kicad_sch`, `.kicad_pcb`; sau khi sửa phải mở được bằng `kicad-cli` (ERC/DRC chạy được).
5. Mọi thay đổi qua ERC, DRC và kiểm từng chân trước khi người xem: chân nguồn và GND lặp, exposed pad, xung đột pin-mux, nhãn net trùng.
6. IC từ khoảng 100 chân trở lên: làm theo từng khối chân, bắt buộc có bảng đối chiếu từng chân với datasheet.
7. Mỗi lần sửa nhỏ (vài linh kiện hoặc một khối) và xem diff.
8. Routing tốc độ cao, stackup, trở kháng: giao bộ tối ưu chuyên dụng hoặc người; agent viết ràng buộc và đọc báo cáo.
9. Người quyết: kiến trúc và linh kiện chính, cách hiểu ràng buộc, mọi thứ liên quan an toàn điện, chiến lược EMC và chứng nhận, trả lời EQ, đặt hàng.
10. Mỗi giá trị agent báo cáo phải ghi rõ là "tra từ nguồn" hay "suy ra".
11. Thư viện tải về (SnapMagic, Ultra Librarian, SamacSys) coi là chưa kiểm cho tới khi đối chiếu chân, pad, gốc toạ độ và mô hình 3D với datasheet.

Checklist bring-up mặc định của pack đi theo trình tự: soi bằng mắt và đo điện trở rail → cấp nguồn có giới hạn dòng → bật từng rail → nhiệt → áp tại chân IC → clock → JTAG/SWD, UART → chức năng ([research.md §1.4](research.md#14-bring-up)).

## Mô tả theo mô hình core (phác thảo)

Phác thảo `domain.toml` theo [core-model §5](../../docs/core-model.md#5-mô-tả-bằng-file); chỉ một phần, để thấy các khái niệm áp vào domain này thế nào.

```toml
name = "pcb-design"

[[artefact]]
id = "schematic";  store = "git";  revert = "rev mới"
[[artefact]]
id = "layout";     store = "git";  revert = "rev mới"
[[artefact]]
id = "bom";        store = "git";  origin = "generated+edited"   # sinh từ schematic, phần sửa tay để riêng
[[artefact]]
id = "fab-package"; store = "git";  origin = "generated";  derived_from = ["layout"]
[[artefact]]
id = "pin-map";    store = "git";  owner = "pcb-design";  shared_with = ["embedded-mcu"]
[[artefact]]
id = "board-outline"; store = "git";  owner = "mechanical-design";  shared_with = ["pcb-design"]

[[source]]
id = "datasheets";  access = "grep";  precision = "exact"
[[source]]
id = "fab-rules";   access = "grep";  precision = "exact"     # kèm .kicad_dru ghim phiên bản
[[source]]
id = "distributor-stock";  access = "query";  freshness = "lúc dùng"
[[source]]
id = "bringup-log";  access = "grep";  kind = "runtime";  key = ["rev", "serial"]

[[step]]
id = "drc";  kind = "check";  speed = "fast"
evidence = { type = "binary", command = "kicad-cli pcb drc --schematic-parity --exit-code-violations --format json" }
on_unavailable = "blocked"

[[step]]
id = "bom-release";  kind = "check";  speed = "fast";  cost = "api-quota"
evidence = { type = "metric", metric = "parts_without_stock", threshold = "== 0" }
on_unavailable = "blocked"

[[step]]
id = "bringup";  kind = "check";  speed = "slow";  cost = "fab + bench"
evidence = { type = "metric", per = "serial" }
on_unavailable = "blocked"

[[loop]]
from = "bringup-log";  to = "errata";  via = "curator"
```

Các trường `origin`, `derived_from`, `owner`, `shared_with`, `freshness`, `key` chưa có trong core-model v0.2; chúng là đề xuất từ [thử giấy doc-types-pcb](../../docs/paper-tests/doc-types-pcb.md) (P4, P5, P6, P7, P10) và cần chốt ở core trước khi dùng.

## So với hai domain đã có

| | `embedded-mcu` | `llm-agent` | `pcb-design` |
| --- | --- | --- | --- |
| Artefact | firmware trong git | code, prompt, cấu hình, model | schematic, layout, BOM, thư viện (file EDA trong git) |
| Kiểm chứng nhanh | build, test, bộ nhớ | lint, unit | ERC, DRC/parity, BOM qua API |
| Kiểm chứng chậm | HIL bench | eval chậm | sản xuất + bring-up (nhiều tuần, tiền thật) |
| Số lần thực hiện | một | một | ba nối tiếp (schematic, placement, routing) |
| Sau phát hành | OTA theo đợt, rollback | canary, rollback | không rollback: rework hoặc rev mới |
| Nguồn lỗi thật | telemetry, coredump | trace hội thoại, khiếu nại | số đo bring-up theo serial, lỗi lắp ráp, EQ của nhà máy |
| Tri thức đổi theo thời gian | errata chip | API, model | tồn kho, giá, vòng đời linh kiện |

Cả ba gói dùng cùng các khái niệm của mô hình khái quát; khác nhau ở giá trị, không ở cấu trúc.

## Ghi chú

- Tiêu chuẩn IPC và IEC có bản quyền: chỉ dùng nội bộ, skill chỉ giữ mã điều khoản và diễn giải do nhóm tự viết.
- Cổng kiểm dựng trên `kicad-cli` và đọc file S-expression, không dựa vào API Python: API SWIG cũ sắp bị gỡ, API IPC mới cần giao diện đang chạy và chưa phủ schematic.
- Bước chạy được mà không cần board thật (ERC, DRC, parity, kiểm BOM, tính toán, xuất gói) là phần agent tự làm được nhiều nhất; ba cổng duyệt, trả lời EQ và bring-up cần người.
- Sơ đồ 02 không vẽ mũi tên quay lại của ERC lỗi và placement bị từ chối (vướng giới hạn bố cục của archify); hai đường này ghi trong thẻ "Đường quay lại".
- Tên agent, vị trí cổng duyệt và các công cụ là đề xuất, chưa chốt.

## Câu hỏi còn mở

- Nhóm có cần cổng duyệt placement riêng không, hay gộp vào chốt gửi sản xuất cho board đơn giản (2 lớp, không tốc độ cao)? Đề xuất: bước có `when`, chỉ bắt buộc khi board có nguồn công suất, RF, tốc độ cao hoặc đổi biên cơ khí.
- Thiết kế dạng code (atopile, SKiDL) hay KiCad thuần? Bằng chứng cho thấy agent làm tốt hơn trên dạng code, nhưng nhóm phần cứng quen KiCad GUI. SKiDL chỉ sinh netlist (hoặc `.kicad_pcb` chỉ có footprint), không tự placement hay routing, và không có back-annotation: sửa trong layout không chảy ngược về code Python ([caveats](https://skidl.readthedocs.io/en/latest/caveats.html)). Chưa chốt.
- Nhà máy chính (JLCPCB, PCBWay hay nhà máy trong nước) quyết định file `.kicad_dru`, định dạng gói (Gerber hay IPC-2581) và API linh kiện mặc định của pack.
- Trạng thái theo mục trong errata và thư viện (P11), lý do cho luật máy đọc (P13): giữ như câu hỏi mở của [thử giấy](../../docs/paper-tests/doc-types-pcb.md#53-thay-đổi-nhỏ-nhất-chỉ-là-khuyến-nghị).
