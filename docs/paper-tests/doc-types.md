---
id: PT-DOC-TYPES
type: report
form: paper-test
status: reviewed
origin: authored
---

# Thử giấy: bộ loại tài liệu của core trên domain nhúng và cơ khí

Mục đích: xếp mọi tài liệu mà hai domain `embedded-mcu` và `mechanical-design` tạo ra hoặc dùng vào **6 loại** đề xuất ở bản đầu của [research/doc-standards.md §6.1](../research/doc-standards.md#61-hai-trục-type-và-form) (mục đó đã được viết lại theo kết luận của bài thử này), **không được thêm loại**. Chỗ nào không xếp được là lỗ hổng của đề xuất.

6 loại đem thử: `specification`, `description`, `decision`, `procedure`, `report`, `issue`. Hai loại tuỳ chọn `reference` và `explanation` được dùng nhưng ghi là "Một phần", vì đề xuất coi chúng là phụ.

**Đầu vào:** chưa có dự án thật nào của hai domain. Danh sách tài liệu lấy từ mô tả domain pack và sơ đồ vòng lặp: [embedded-mcu](../../domains/embedded-mcu/README.md) (sơ đồ 02) và [mechanical-design](../../domains/mechanical-design/README.md) (sơ đồ 02). Đây là tài liệu **theo thiết kế**, chưa phải tài liệu đã viết. Bài thử vì vậy chỉ phát hiện lỗ hổng về loại, chưa phát hiện được lỗ hổng về mẫu chi tiết.

Thang đánh giá: **Vừa** (xếp được, mẫu dùng được nguyên), **Một phần** (xếp được nhưng mẫu phải đổi), **Không** (không loại nào chứa được).

## 1. Domain `embedded-mcu`

| # | Tài liệu | Ở bước | Xếp vào | Kết quả | Lỗ hổng |
| --- | --- | --- | --- | --- | --- |
| E1 | Yêu cầu tính năng (ticket + tiêu chí xong) | `req` | `issue`? | **Không.** Mẫu `issue` là triệu chứng → nguyên nhân → cách xử lý, dành cho lỗi. Yêu cầu tính năng là một đề nghị thay đổi | G1 |
| E2 | Spec + thiết kế module (planner) | `design` | `specification` + `description` | **Một phần.** Một file chứa hai loại; 15289 cho phép gộp, nhưng frontmatter chỉ có một `type` | G2 |
| E3 | Tài liệu đi kèm code (builder viết "code + doc") | `make` | `reference` | **Một phần.** Ở domain này là bắt buộc, không phụ. Một phần được sinh từ code (Doxygen) | G3 |
| E4 | Kết quả kiểm nhanh: log build, báo cáo bộ nhớ so với base | `check` | `report` | **Vừa** | |
| E5 | Kết quả review theo checklist | `check` | `report` | **Một phần.** Mẫu `report` giả định sinh từ `verify.py`; đây là bằng chứng phán đoán do agent hoặc người viết | G13 |
| E6 | Log HIL, số đo dòng | `check` | `report` (bản ghi đính kèm) | **Vừa** | |
| E7 | Phán quyết của verifier | `check` | `report` | **Vừa** | |
| E8 | Duyệt thiết kế, duyệt merge | `decide` | `decision` | **Một phần.** ADR (bối cảnh, quyết định, hệ quả) quá nặng cho một lần duyệt. Thứ cần ghi chỉ là: ai duyệt, duyệt phiên bản nào, dựa trên bằng chứng nào | G4 |
| E9 | Kế hoạch OTA theo đợt; chính sách HIL | `release`, `check` | — | **Không.** Core không có loại kế hoạch (15289: plan) | G5 |
| E10 | Telemetry, crash từ hiện trường | `observe` | (bản ghi) | **Một phần.** Không phải tài liệu viết tay; chỉ cần được trỏ tới | G3 |
| E11 | Quyết định giữ hay rollback | `decide` | `report` | **Vừa** | |
| E12 | Lỗi đã biết (chuỗi log → nguyên nhân → trạng thái) | `learn` | `issue` | **Vừa.** Khớp hoàn toàn với mẫu troubleshooting | |
| E13 | `refs/SOURCES.md`, `decisions.md` dạng một file nhiều mục | tri thức | `reference`, `decision` | **Một phần.** Đây là **sổ** (nhiều mục trong một file), còn mẫu đề xuất là một tài liệu cho mỗi mục | G6 |
| E14 | `CLAUDE.md`, checklist review | bản đồ | — | **Không.** Là quy tắc bắt buộc (15289: policy), không thuộc 6 loại | G5 |
| E15 | Khi bật SIL/ASIL: phân tích mối nguy, ma trận truy vết | `design`, `check` | `report` | **Một phần.** Phân tích mối nguy vừa. Ma trận truy vết không nên viết tay mà sinh từ trường `traces` | G7 |
| E16 | Pin map, power tree (dùng chung với `pcb-design`) | `design` | `specification` | **Một phần.** Hai domain cùng sở hữu một tài liệu; đề xuất chưa có cách ghi chủ sở hữu và bên dùng | G8 |
| E17 | Phiên bản phát hành OTA (firmware nào chạy trên đợt nào) | `release` | — | **Không.** Cần ghi một **baseline**: các artefact và phiên bản tại một thời điểm | G14 |

## 2. Domain `mechanical-design`

| # | Tài liệu | Ở bước | Xếp vào | Kết quả | Lỗ hổng |
| --- | --- | --- | --- | --- | --- |
| M1 | Yêu cầu vỏ (PCB, kích thước, IP, giá) | `req` | `specification` | **Một phần.** Yêu cầu phần lớn là **bảng thông số có dung sai**, không phải câu. Luật EARS không áp được | G9 |
| M2 | Chia mảnh, vật liệu, cách lắp (planner) | `design` | `description` | **Một phần.** Mẫu arc42 rút gọn + C4 thiên về phần mềm ("container", "component") | G10 |
| M3 | Duyệt kiểu dáng (hình khối, màu, bề mặt) | `decide` | `decision` | **Một phần.** Giống E8, thêm bằng chứng là hình ảnh và mẫu vật lý | G4, G11 |
| M4 | Bản vẽ kỹ thuật (ISO 128/129, khung tên ISO 7200) | `make` | `specification` | **Một phần.** Bản vẽ là đặc tả để sản xuất, nhưng không phải Markdown. Khung tên đóng vai frontmatter; `doclint` không đọc được | G12 |
| M5 | BOM cơ khí, bảng CMF | `make` | `reference` | **Một phần.** Bảng tính, cùng vấn đề định dạng với M4 | G12 |
| M6 | Kết quả kiểm hình học | `check` | `report` | **Vừa** | |
| M7 | Kết quả FEA (thử rơi, ứng suất lẫy gài) | `check` | `report` | **Một phần.** Không ghi trường hợp tải, điều kiện biên, lưới thì con số không kiểm lại được. Mẫu `report` chưa có mục phương pháp và giả định | G13 |
| M8 | Review DFM, lắp ráp, an toàn | `check` | `report` | **Một phần.** Giống E5 | G13 |
| M9 | Kết quả mẫu in 3D (lắp thử, nút, cổng) | `check` | `report` | **Một phần.** Bằng chứng là ảnh và nhận xét cầm nắm | G11 |
| M10 | Chốt thiết kế trước khi làm khuôn | `decide` | `decision` | **Không.** Thứ cần ghi là baseline (mọi file CAD, bản vẽ, BOM ở phiên bản nào) cộng với một lần duyệt | G4, G14 |
| M11 | Đặt khuôn; báo cáo DFM và báo cáo T1 của nhà làm khuôn | `release` | — | **Không.** Tài liệu do **bên ngoài** viết. Phải giữ nguyên làm nguồn, không viết lại | G15 |
| M12 | Kết quả T1 (rơi, IP theo IEC 60529, ngoại quan) | `check` | `report` | **Vừa.** Trường `standard` dùng đúng chỗ | |
| M13 | Lỗi từng lần mẫu | `learn` | `issue` | **Vừa** | |
| M14 | Luật DFM nội bộ rút ra từ lỗi | `learn` | — | **Không.** Là quy tắc bắt buộc, giống E14 | G5 |
| M15 | Sửa khuôn bớt thép (ECO) | `make` | `issue`? | **Không.** Đề nghị thay đổi kèm phân tích ảnh hưởng, giống E1 | G1 |

## 3. Tổng hợp

| Kết quả | `embedded-mcu` | `mechanical-design` | Tổng |
| --- | --- | --- | --- |
| Vừa | 6 | 3 | 9 |
| Một phần | 7 | 8 | 15 |
| Không | 4 | 4 | 8 |
| **Cộng** | 17 | 15 | 32 |

Chỉ 9/32 tài liệu vừa nguyên với mẫu. Các tài liệu vừa tập trung ở `report` và `issue`, tức là phần kiểm chứng và phần học lại. Phần đầu vòng lặp (yêu cầu, thiết kế) và phần cổng duyệt hầu như đều lệch.

## 4. Lỗ hổng

| ID | Lỗ hổng | Xuất hiện ở | Loại lỗ hổng |
| --- | --- | --- | --- |
| G1 | Thiếu loại **request**: yêu cầu tính năng, ECO, change request | E1, M15 | thiếu loại (15289 có) |
| G2 | Một file chứa nhiều loại | E2 | trường `type` quá cứng |
| G3 | Tài liệu sinh tự động và bản ghi không phải tài liệu viết tay | E3, E10 | chưa phân biệt nguồn gốc |
| G4 | Thiếu bản ghi **duyệt** nhẹ: ai, phiên bản nào, bằng chứng nào, kết luận | E8, M3, M10 | thiếu mẫu; liên quan nguyên lý 3 của core |
| G5 | Thiếu **plan** và **policy** (kế hoạch, quy tắc, checklist) | E9, E14, M14 | thiếu loại (15289 có) |
| G6 | Sổ nhiều mục trong một file | E13 | mẫu chỉ có dạng một tài liệu |
| G7 | Ma trận truy vết phải sinh, không viết tay | E15 | đúng hướng, cần ghi rõ |
| G8 | Tài liệu dùng chung giữa hai domain | E16 | thiếu trường sở hữu |
| G9 | Đặc tả dạng bảng thông số có dung sai | M1 | mẫu và luật lint quá thiên về phần mềm |
| G10 | Mẫu `description` (arc42, C4) thiên về phần mềm | M2 | mẫu không trung lập |
| G11 | Bằng chứng là hình ảnh hoặc mẫu vật lý | M3, M9 | thiếu cách trỏ tới bằng chứng không phải văn bản |
| G12 | Tài liệu không phải Markdown (bản vẽ, bảng tính) | M4, M5 | `doclint` và frontmatter giả định Markdown |
| G13 | `report` chưa có mục **phương pháp và giả định**; chưa phân biệt báo cáo sinh tự động và báo cáo phán đoán | E5, M7, M8 | mẫu thiếu mục |
| G14 | Thiếu **baseline**: tập artefact và phiên bản tại một cổng | E17, M10 | thiếu mẫu; ISO 10007 |
| G15 | Tài liệu của bên ngoài | M11 | chưa phân biệt nguồn gốc (giống G3) |

## 5. Kết luận: sửa đề xuất thế nào

Phần lớn lỗ hổng (G1, G2, G4, G5, G6, G9, G10, G13, G14) có chung một nguyên nhân: đề xuất dùng **một trường** cho hai việc khác nhau. Việc thứ nhất là phân loại để so sánh giữa các domain. Việc thứ hai là chọn mẫu và luật lint. Cách sửa theo đúng nguyên tắc "khái quát, không liệt kê" của [core-model.md §1](../core-model.md#1-nguyên-tắc-thiết-kế) là tách thành hai trục:

1. **`type`: đúng 7 loại của 15289 cộng `record`**, không tự đặt thêm. Trục này dùng để phân loại và so sánh, nên đủ nhỏ và ổn định cho core. Riêng trục này đã giải quyết G1 và G5. G2 được giải quyết bằng cách cho `type` nhận một danh sách.
2. **`form`: mẫu cụ thể**, tức thứ quyết định mục bắt buộc và luật lint. Core chỉ có vài `form` trung lập. Domain pack thêm `form` của ngành:

   | `form` | `type` | Ở đâu | Giải quyết |
   | --- | --- | --- | --- |
   | `change-request` | request | core | G1 |
   | `known-failure` | request hoặc record | core (chính là `issue` cũ) | |
   | `adr` | description (lý do thiết kế) | core | |
   | `approval` | record | core: ai, phiên bản hoặc hash, bằng chứng, kết luận, ngày | G4 |
   | `baseline` | record | core: danh sách artefact và phiên bản tại một cổng | G14 |
   | `verify-report` | report | core, sinh từ `verify.py` | |
   | `review-report` | report | core: phương pháp, phát hiện, kết luận phán đoán | G13 |
   | `howto` | procedure | core | |
   | `register` | bất kỳ | core: một file nhiều mục, mỗi mục có ID | G6 |
   | `ears-spec` | specification | domain pack phần mềm, nhúng | |
   | `param-spec` | specification | domain pack phần cứng: bảng thông số có dung sai | G9 |
   | `drawing` | specification | `mechanical-design`, metadata đọc từ khung tên | G12 |
   | `sim-report` | report | `mechanical-design`: trường hợp tải, điều kiện biên, lưới, kết quả | G13 |

   G10 được giải quyết bằng cách để mẫu `description` của core chỉ có 4 mục trung lập: mục tiêu, ngữ cảnh, phân rã, giao diện. arc42 và C4 thành `form` của domain phần mềm.

3. **Thêm vào frontmatter chung ba trường** cho các lỗ hổng còn lại:
   - `origin = authored | generated | external`. Với `generated` và `external`, agent không được sửa nội dung, chỉ được trỏ tới (G3, G15).
   - `owner_domain` và `shared_with` (G8).
   - `evidence` nhận đường dẫn tới file bất kỳ: ảnh, video, mô hình STEP, mã số mẫu vật lý (G11).
4. **Metadata của file không phải Markdown** được khai báo trong profile, bằng file đi kèm (`<file>.meta.toml`) hoặc bằng cách đọc từ chính file (khung tên, thuộc tính bảng tính). `doclint` chỉ kiểm phần metadata, không kiểm nội dung (G12).
5. **Ma trận truy vết** không phải một loại tài liệu. Nó là một view sinh từ trường `traces`, giống cách [core-model.md §6](../core-model.md#6-tổng-quan-sinh-từ-mô-tả) sinh sơ đồ từ mô tả (G7).

Sau khi sửa như trên, xếp lại thử 32 tài liệu trên giấy: cả 32 đều có `type` và `form`. Lần xếp lại này do chính người viết đề xuất làm, nên chưa phải bằng chứng độc lập. Cần thử lại trên một domain thứ ba chưa nhìn tới (ví dụ `pcb-design`) và trên tài liệu viết thật.

## 6. Việc tiếp theo

- Cập nhật [research/doc-standards.md §6](../research/doc-standards.md#6-đề-xuất-thiết-kế-cho-archwright) theo hai trục `type` / `form` khi đề xuất được duyệt.
- Thử giấy lần hai trên `pcb-design`, không sửa đề xuất trong lúc thử.
- Viết mẫu cho `approval` và `baseline` trước. Đây là hai mẫu lấp chỗ trống lớn nhất (G4, G14), và gắn trực tiếp với nguyên lý "người giữ quyền quyết" của core.
