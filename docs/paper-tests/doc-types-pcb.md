---
id: PT-DOC-TYPES-PCB
type: report
form: paper-test
status: reviewed
origin: authored
---

# Thử giấy: phân loại tài liệu hai trục `type` / `form` trên domain `pcb-design`

## 1. Mục đích và đầu vào

Thử giấy đề xuất ở [research/doc-standards.md §6.1–6.2](../research/doc-standards.md#61-hai-trục-type-và-form): trục `type` (7 loại của ISO/IEC/IEEE 15289 cộng `record`) và trục `form` (mẫu cụ thể, core có 11 form, domain pack khai thêm bằng `[[doc_form]]`). Mục tiêu là tìm lỗ hổng, không xác nhận đề xuất. Đề xuất không được sửa trong lúc thử.

Đầu vào:

- [domains/pcb-design/README.md](../../domains/pcb-design/README.md) và hai nguồn sơ đồ [01-overview.architecture.json](../../domains/pcb-design/src/01-overview.architecture.json), [02-feature-loop.workflow.json](../../domains/pcb-design/src/02-feature-loop.workflow.json).
- Phần artefact chung trong [domains/embedded-mcu/README.md](../../domains/embedded-mcu/README.md) (pin map, power tree) và [domains/mechanical-design/README.md](../../domains/mechanical-design/README.md) (biên PCB, lỗ bắt vít, vị trí cổng và nút).
- [core-model.md](../core-model.md) cho các khái niệm.

Lưu ý: các nguồn trên là **mô tả lúc thiết kế** của gói sơ đồ, không phải tài liệu của một dự án PCB thật. Danh sách tài liệu dưới đây dựng từ nhãn và ghi chú của sơ đồ. Mục ghi "suy ra" là tài liệu kỹ sư chắc chắn cần cho vòng lặp này nhưng sơ đồ không nêu. Lần thử này độc lập, không dùng kết quả thử giấy trước.

Tên chuẩn ngành nhắc trong file (IPC-2581, IPC-2612, IEC 81346, IPC-A-610, IEC 61000) đều **[chưa kiểm]**, chỉ nêu tên.

Cách chấm:

- **Vừa**: xếp được vào một form của core như đang viết, hoặc vào một form của pack khai đúng các trường `[[doc_form]]` cho phép (`id`, `type`, `template`, `required_sections`, `lint`, `files`, `meta_from`, `extends`, `standard`) và frontmatter chung.
- **Một phần**: diễn đạt được nhưng phải uốn: nhét thông tin vào thân bài mà máy không kiểm được, dùng form sai mục đích, hoặc cơ chế không nói rõ.
- **Không**: không diễn đạt được.

## 2. Bảng phân loại

| # | Tài liệu | Ở bước | type | form | Kết quả | Lỗ hổng |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Yêu cầu board (chức năng, kích thước, giá) | Yêu cầu board | specification | pack `board-req` (dạng `param-spec`) | Vừa | |
| 2 | Kiến trúc khối | planner | description | `design-note` | Vừa | |
| 3 | Power tree | planner | specification, description | pack `power-tree`, `shared_with: [embedded-mcu]` | Một phần | P10 |
| 4 | Pin map | builder schematic | specification | pack `pin-map` (CSV + sidecar) | Một phần | P4, P5, P10 |
| 5 | Quyết định chọn linh kiện chính | planner, duyệt kiến trúc | description | `adr` trong `register` (`decisions.md`) | Vừa | |
| 6 | Ước tính giá BOM sơ bộ | duyệt kiến trúc | report | pack `cost-estimate` | Một phần | P6 |
| 7 | Phê duyệt kiến trúc | duyệt kiến trúc | record | `approval` | Vừa | |
| 8 | Tính toán và mô phỏng (SPICE, nguồn, độ rộng đường mạch, nhiệt) | Mô phỏng | report | pack `sim-report` | Vừa | |
| 9 | Schematic (`.kicad_sch`, nhiều sheet) | builder schematic | specification, description | pack `schematic`, `meta_from = "title-block"` | Một phần | P1, P2, P3, P15 |
| 10 | BOM (MPN, linh kiện thay thế, DNP) | builder schematic | specification | pack `bom` (CSV + sidecar) | Một phần | P4, P5, P6, P8 |
| 11 | Thư viện symbol/footprint đã kiểm | builder, curator | specification, record | pack `part-library` hoặc `register` | Một phần | P2, P11 |
| 12 | Báo cáo ERC (file `.rpt`/JSON của KiCad CLI làm bằng chứng) | ERC | report | `verify-report` | Vừa | |
| 13 | Báo cáo kiểm BOM (tồn kho, vòng đời, giá) | kiểm BOM | report | `verify-report` | Một phần | P6 |
| 14 | Waiver: vi phạm ERC/DRC được chấp nhận có lý do (suy ra) | ERC, DRC | record, request | không có; uốn `approval` | Một phần | P9 |
| 15 | Checklist chốt schematic (mẫu) | chốt schematic | policy | `rules` | Vừa | |
| 16 | Checklist chốt schematic đã điền | chốt schematic | report | `review-report` | Vừa | |
| 17 | Baseline và phê duyệt chốt schematic | chốt schematic | record | `baseline` + `approval` | Vừa | |
| 18 | Layout (`.kicad_pcb`) và stackup | builder layout | specification | pack `layout`, `meta_from = "title-block"` | Một phần | P2, P3, P15 |
| 19 | Luật thiết kế máy đọc (`.kicad_dru`, net class) | builder layout, DRC | policy | `rules` | Một phần | P13 |
| 20 | Luật DFM và năng lực nhà sản xuất (tài liệu của nhà máy) | DRC, DFM | policy, specification | pack `fab-capability`, `origin: external`, sidecar | Vừa | |
| 21 | Báo cáo DRC | DRC | report | `verify-report` | Vừa | |
| 22 | Báo cáo DFM của công cụ nội bộ | DFM | report | `verify-report` | Vừa | |
| 23 | Review layout (nguồn, EMC) | reviewer | report | `review-report` | Vừa | |
| 24 | Gói sản xuất mạch in (Gerber, drill, hoặc IPC-2581) | chốt gửi sản xuất | specification | pack `fab-package`, `origin: generated` | Một phần | P2, P5 |
| 25 | Bản vẽ sản xuất, fab notes (vật liệu, độ dày, trở kháng, cấp IPC) | chốt gửi sản xuất | specification | pack `drawing`, `meta_from = "title-block"` | Vừa | |
| 26 | Gói lắp ráp (pick-and-place, bản vẽ lắp ráp, BOM lắp ráp) | chốt gửi sản xuất | specification | pack `assembly-package`, `origin: generated` | Một phần | P2, P5, P8 |
| 27 | Báo giá và thời gian giao của nhà máy | chốt gửi sản xuất | record | pack `quote`, `origin: external` | Một phần | P6 |
| 28 | Baseline và phê duyệt gửi sản xuất (Gerber, BOM, giá) | chốt gửi sản xuất | record | `baseline` + `approval` | Vừa | |
| 29 | Đơn đặt hàng (suy ra) | đặt hàng | request | pack `purchase-order` | Vừa | |
| 30 | Câu hỏi kỹ thuật của nhà máy (EQ) và câu trả lời (suy ra) | sản xuất | request, record | không có; uốn `change-request` | Một phần | P14 |
| 31 | Tài liệu nhà máy giao kèm lô (CoC, e-test, coupon trở kháng) (suy ra) | sản xuất | record, report | pack `fab-record`, `origin: external` | Một phần | P7 |
| 32 | Checklist bring-up | verifier | procedure, plan | `howto` | Vừa | |
| 33 | Số đo bring-up thô (CSV, ảnh dao động ký, ảnh nhiệt) | sản xuất + bring-up | record | pack `bench-log`, ảnh trong `evidence` | Một phần | P7 |
| 34 | Báo cáo bring-up PASS/FAIL | verifier | report | `verify-report` | Một phần | P1, P7 |
| 35 | Errata của rev | curator | record | `register` các mục `known-failure` | Một phần | P1, P11, P12 |
| 36 | Lỗi board, lỗi lắp ráp đã biết | curator | record | `known-failure` | Một phần | P12 |
| 37 | Hướng dẫn rework | curator | procedure | `howto` | Vừa | |
| 38 | Nhật ký rework từng board (suy ra) | curator | record | `register` | Một phần | P7 |
| 39 | ECO, danh sách thay đổi cho rev sau | curator → planner | request | `change-request` | Vừa | |
| 40 | Lịch sử rev (suy ra) | curator | record | `register`, mỗi mục một rev | Vừa | |
| 41 | Yêu cầu sửa footprint trong thư viện | curator | request | `change-request` | Vừa | |
| 42 | Biên PCB, lỗ bắt vít, vị trí cổng và nút (DXF) | layout, chung với `mechanical-design` | specification | pack `board-outline`, sidecar | Một phần | P5, P10 |
| 43 | Mô hình 3D board (STEP) gửi cơ khí | layout | description | pack `board-3d`, `origin: generated`, `shared_with` | Một phần | P5 |
| 44 | Datasheet linh kiện | Tri thức | specification | pack `datasheet`, `origin: external`, sidecar | Vừa | P17 (chi phí) |
| 45 | `refs/*.txt` trích từ datasheet, DFM | book-to-skill | theo tài liệu gốc | không có form | Một phần | P5 |
| 46 | App note, thiết kế mẫu | Tri thức | description | pack `ref-doc`, `origin: external` | Vừa | |
| 47 | Tiêu chuẩn IPC/IEC (chỉ mã điều khoản và diễn giải nội bộ) | Tri thức | policy | `register` (`SOURCES.md`) + trường `standard` | Vừa | |
| 48 | Skills chuyên ngành (SI/PI, EMC, layout) | Tri thức | description, procedure, policy | pack `skill` | Vừa | |
| 49 | Thông báo EOL/PCN của nhà cung cấp (suy ra) | kiểm BOM | record | pack `supplier-notice`, `origin: external` | Vừa | |
| 50 | Quyết định đổi linh kiện khi hết hàng (verifier trả BLOCKED, người quyết) | chốt schematic, chốt gửi sản xuất | record | `adr` hoặc `approval` | Một phần | P9 |
| 51 | Báo cáo EMC pre-scan (suy ra) | sau bring-up | report | `verify-report` hoặc báo cáo phòng lab `origin: external` | Vừa | |
| 52 | Tồn kho, giá tra lúc dùng | kiểm BOM | không có | không có | Không | P16 |
| 53 | `CLAUDE.md`, luật của domain pack | Domain pack | policy | `rules` | Vừa | |
| 54 | Kế hoạch rev: số lượng board, ngân sách, lịch (suy ra) | planner | plan | pack `build-plan` | Vừa | |

## 3. Tổng kết

| Kết quả | Số tài liệu | Ghi chú |
| --- | --- | --- |
| Vừa | 29 / 54 | 19 vào form của core, 10 vào form pack khai đúng cơ chế |
| Một phần | 24 / 54 | |
| Không | 1 / 54 | tồn kho, giá tra lúc dùng (#52) |

Trục `type` không gây vấn đề nào: cả 53 tài liệu là tài liệu đều gán được một hoặc vài trong 8 giá trị. Mọi lỗ hổng nằm ở trục `form`, ở frontmatter chung và ở cơ chế cho file không phải Markdown.

## 4. Lỗ hổng

| ID | Mô tả | Ở đâu | Loại |
| --- | --- | --- | --- |
| P1 | Frontmatter chung không có trường phiên bản hay rev. Ở PCB, rev là trục chính: BOM theo rev, errata theo rev, báo cáo bring-up cho rev nào. Chỉ `approval` và `baseline` ghi phiên bản của đối tượng | #9, #34, #35 | thiếu trường |
| P2 | Một tài liệu gồm nhiều file (schematic phân cấp, bộ Gerber + drill, gói lắp ráp, thư viện). `files` là glob nhưng không nói mỗi file là một tài liệu hay cả tập là một tài liệu; sidecar `<file>.meta.toml` chỉ gắn với một file | #9, #11, #18, #24, #26 | cơ chế mơ hồ |
| P3 | `meta_from = "title-block"` chỉ là một từ khoá. Không khai cách ánh xạ ô của khung tên KiCad (rev, ngày, comment) sang `id`, `type`, `status`, `traces` | #9, #18 | thiếu đặc tả |
| P4 | `origin` chỉ một giá trị. BOM và pin map thường sinh từ schematic rồi sửa tay (linh kiện thay thế, DNP, tên tín hiệu cho firmware). Ghi `generated` thì agent không được sửa; ghi `authored` thì mất quan hệ với nguồn sinh | #4, #10 | thiếu giá trị |
| P5 | Không có quan hệ "dẫn xuất từ". Gerber, gói lắp ráp, STEP, pin map, `refs/*.txt` đều sinh từ một tài liệu khác. Không có trường này thì không phát hiện được đầu ra cũ hơn nguồn (Gerber cũ hơn layout). `sources` dành cho con số, `traces` dành cho truy vết; cả hai đều không nói rõ quan hệ này | #4, #10, #24, #26, #42, #43, #45 | thiếu quan hệ |
| P6 | Không có ngày hiệu lực của nội dung (`as_of`, `valid_until`). Giá, tồn kho, vòng đời, báo giá đổi theo tuần. core-model có "độ tươi" cho nguồn tri thức, nhưng frontmatter tài liệu không có | #6, #10, #13, #27 | thiếu trường |
| P7 | Không có định danh bản thể vật lý (số serial board, lô sản xuất). Số đo bring-up, nhật ký rework, CoC đều gắn với một board hay một lô cụ thể, không chỉ với rev | #31, #33, #34, #38 | thiếu khái niệm |
| P8 | Không có biến thể lắp ráp (variant, DNP). Một schematic có thể sinh vài BOM và gói lắp ráp khác nhau (suy ra) | #10, #26 | thiếu trường |
| P9 | Không có form cho waiver/deviation: chấp nhận một vi phạm luật hay thay linh kiện tạm cho một lô, có phạm vi, lý do, người duyệt, hạn. `approval` thiếu "luật nào bị miễn" và "phạm vi áp dụng" | #14, #50 | thiếu form core |
| P10 | Tài liệu chung giữa domain: `owner_domain` và `shared_with` chỉ là nhãn. Không nói form khai ở pack nào khi cả hai pack cần kiểm, ai được sửa, và thay đổi có cần phê duyệt của mọi domain trong `shared_with` hay không. (`approval` đã cho phép nhiều người duyệt; thứ còn thiếu là luật bắt buộc phải có người duyệt của từng domain) | #3, #4, #42 | thiếu luật |
| P11 | `status`, `sources`, `traces` chỉ ở cấp file. `register` có nhiều mục có ID nhưng không có trạng thái theo mục (footprint đã kiểm hay chưa, errata đã sửa ở rev nào) | #11, #35 | thiếu cấp mục |
| P12 | `known-failure` bắt buộc "triệu chứng (nguyên văn)": giả định triệu chứng là chuỗi log. Ở phần cứng triệu chứng là số đo, ảnh dao động ký, ảnh mối hàn. Errata còn cần "ảnh hưởng rev nào, sửa ở rev nào" | #35, #36 | mục bắt buộc thiên phần mềm |
| P13 | `rules` bắt buộc mỗi quy tắc có ID và lý do. Luật máy đọc (`.kicad_dru`, net class) có tên luật nhưng không có chỗ ghi lý do; sidecar một file không chứa được lý do từng luật | #19 | không hợp file máy |
| P14 | Trao đổi hai chiều với bên ngoài (EQ của nhà máy hỏi, nhóm trả lời) không có form; `change-request` dành cho thay đổi của chính dự án | #30 | thiếu form (pack tự khai được) |
| P15 | Ranh giới artefact và tài liệu không rõ. Schematic và layout vừa là artefact thiết kế vừa là tài liệu. Đề xuất không nói `doclint` có áp lên chúng không; vòng đời `draft → reviewed → approved` trùng với cổng chốt và `baseline` | #9, #18 | ranh giới |
| P16 | Nguồn tra lúc dùng (tồn kho, giá) không phải tài liệu lưu lại. Đề xuất không nói nguồn tri thức nào cần metadata tài liệu, nguồn nào chỉ khai trong core-model | #52 | ranh giới |
| P17 | Hàng trăm datasheet PDF, mỗi file một `.meta.toml`, là chi phí lớn. Cơ chế chỉ có sidecar hoặc `meta_from`, không có cách khai metadata cho nhiều file trong một manifest hay `register` | #44 | chi phí |

## 5. Kết luận

### 5.1. Phần đề xuất đã xử lý được

- Trục `type` đứng vững trên PCB: không tài liệu nào cần loại thứ 9. Tách `type` khỏi `form` là đúng hướng.
- Hai cổng chốt diễn đạt gọn bằng `baseline` + `approval` của core (#17, #28).
- File máy sinh (báo cáo ERC, DRC) vào `verify-report`, file gốc làm `evidence`.
- **P14** xử lý được bằng một form của pack, không cần đổi core.
- **P16** đã có chỗ trong core-model (nguồn tri thức `access = "query"`). Chỉ cần đề xuất nói một câu: nguồn không lưu thành file thì không phải tài liệu.
- **P1** được xử lý một phần: `baseline` và `approval` ghi phiên bản của đối tượng, nhưng tài liệu tự nó không mang rev.
- **P12** có thể xử lý bằng `extends = "known-failure"` ở pack, nếu `extends` được phép đổi mục bắt buộc. Đề xuất chưa nói điều này.

### 5.2. Phần cần đổi

P1, P2, P3, P5, P6, P7, P9, P10, P11 cần thay đổi ở core; P4, P8, P13, P17 cần thay đổi nhỏ hoặc một câu làm rõ. Nhiều lỗ hổng không riêng PCB: rev, dẫn xuất, ngày hiệu lực và waiver cũng xuất hiện ở firmware và cơ khí.

### 5.3. Thay đổi nhỏ nhất (chỉ là khuyến nghị)

1. **Thêm ba trường tuỳ chọn vào frontmatter chung:** `rev` (phiên bản của chính tài liệu hay artefact), `applies_to` (danh sách rev, biến thể hoặc serial mà nội dung áp dụng), `as_of` (ngày của dữ liệu đổi theo thời gian). Xử lý P1, P6, P8 và phần lớn P7, P12.
2. **Làm rõ cơ chế file không phải Markdown:** thêm `unit = "file" | "set"` cho `[[doc_form]]` (một sidecar cho cả tập file), cho phép metadata đến từ một manifest, và thêm trường `derived_from` cho tài liệu sinh ra, kèm quy tắc `origin: generated` + danh sách phần sửa tay. Xử lý P2, P4, P5, P17; P3 cần thêm bảng ánh xạ trong `meta_from`.
3. **Thêm form core `deviation`** (type `record` + `request`: luật hoặc yêu cầu bị miễn, phạm vi, lý do, hạn, người duyệt) **và một luật cho tài liệu chung:** thay đổi tài liệu có `shared_with` cần phê duyệt của `owner_domain` và mỗi domain trong `shared_with`; `approval` đã cho phép nhiều người duyệt, chỉ cần thêm luật kiểm cho trường hợp này. Xử lý P9, P10.

Các điểm còn lại (P11 trạng thái theo mục trong `register`, P13 lý do cho luật máy đọc, P15 ranh giới artefact và tài liệu) nên ghi vào §7 "Câu hỏi còn mở" của đề xuất trước khi sửa.
