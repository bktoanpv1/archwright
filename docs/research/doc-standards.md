---
id: RS-DOC-STANDARDS
type: report
form: research-report
status: draft
origin: authored
---

# Nghiên cứu: chuẩn quốc tế và cấu trúc tài liệu tinh gọn cho agent viết tài liệu

Ngày: 2026-10-29. Trạng thái: nghiên cứu, chưa hiện thực.

Mục đích: chọn bộ chuẩn và cấu trúc tài liệu đủ nhỏ để đưa vào core của archwright, và phần nào để domain pack thay. Bối cảnh: [architecture.md](../architecture.md), [core-model.md](../core-model.md).

Ký hiệu nguồn: **[đã kiểm]** là thông tin có nguồn trong mục Nguồn ở cuối. **[chưa kiểm]** là thông tin lấy từ hiểu biết chung, cần đối chiếu bản chuẩn hiện hành trước khi dùng. Phần lớn chuẩn ISO/IEC/IEEE phải mua; tài liệu này chỉ ghi tên chuẩn và tên điều khoản, không chép nội dung.

## 1. Kết luận ngắn

1. Chuẩn quốc tế về tài liệu chia thành **ba lớp** khác nhau. Agent cần cả ba, nhưng mỗi lớp được kiểm chứng theo một cách:

   | Lớp | Câu hỏi | Chuẩn gốc | Kiểm được tự động? |
   | --- | --- | --- | --- |
   | A. Danh mục | Dự án cần **những tài liệu nào**? | ISO/IEC/IEEE 15289 (7 loại tài liệu chung + bản ghi) | Có: có hay không có file |
   | B. Nội dung | Mỗi tài liệu cần **những mục nào**? | 29148, 42010, IEEE 1016, 26514, 82079-1, 29119-3 | Một phần: đủ mục, đủ trường |
   | C. Câu chữ | Viết **câu** thế nào? | ASD-STE100, INCOSE GtWR, EARS, nguyên tắc tối giản của 82079-1 | Một phần: luật đo được qua lint |

2. Các chuẩn ở lớp B rất nặng. Có **cấu trúc tinh gọn** dùng được thay thế, đã được nhiều dự án dùng: Diátaxis, kiểu topic của DITA, mẫu của The Good Docs Project, ADR (Nygard/MADR), arc42 rút gọn, C4, EARS.

3. **Không nên tạo một agent mới.** [architecture.md §4](../architecture.md#4-agent-4-vai-trò-chung-chuyên-môn-hoá-bằng-checklist) đã quyết rằng chuyên môn nằm ở checklist, `verify.toml` và skill. Vì vậy "agent chuẩn hoá tài liệu" nên là ba thứ:
   - một skill `doc-standard` mà `curator` và `builder` dùng khi viết;
   - một bước `check` tên `doclint` trong vòng kiểm chứng;
   - một **doc profile** trong domain pack để chọn loại tài liệu và chuẩn của ngành.

4. Phần kiểm được tự động chỉ là **hình thức**: đủ mục, câu yêu cầu đúng mẫu, con số có nguồn, liên kết truy vết còn sống. **Nội dung đúng hay sai** vẫn là bằng chứng dạng phán đoán do người hoặc rubric chấm. Agent không được tự nói PASS ở phần này, đúng nguyên lý 1 và 3 của [core-model.md §4](../core-model.md#4-thứ-bất-biến-duy-nhất-nguyên-lý-không-phải-cấu-trúc).

## 2. Lớp A: danh mục tài liệu (ISO/IEC/IEEE 15289)

ISO/IEC/IEEE 15289 (bản 2019 là bản hiện hành) định nghĩa nội dung tài liệu theo **loại chung** và theo mục đích cụ thể **[đã kiểm]**. Có 7 loại chung:

| Loại 15289 | Ý nghĩa | Tương ứng trong archwright |
| --- | --- | --- |
| description | mô tả một thứ đang có hoặc sẽ có | tài liệu kiến trúc, thiết kế |
| plan | sẽ làm gì, khi nào, ai làm | kế hoạch giai đoạn, `docs/gates.md` |
| policy | quy tắc bắt buộc của tổ chức | `CLAUDE.md` (phần quy tắc), decisions loại ràng buộc |
| procedure | các bước để làm một việc | hướng dẫn build, flash, vận hành |
| report | kết quả của một hoạt động | báo cáo kiểm chứng (PASS/FAIL/BLOCKED) |
| request | đề nghị một thay đổi | issue, change request |
| specification | yêu cầu phải đạt | đặc tả yêu cầu, giao diện |

Ngoài 7 loại trên, chuẩn có **bản ghi (record)**: dữ liệu thực tế làm bằng chứng cho các loại kia **[đã kiểm]**. Trong archwright, log, trace và kết quả `verify.py` là bản ghi.

Hai điểm làm 15289 hợp với nguyên tắc "mô tả, không quy định":

- Chuẩn chỉ đưa **dàn ý gợi ý**, không bắt buộc từng mục. Tài liệu được **gộp hoặc tách** tuỳ dự án và tổ chức **[đã kiểm]**.
- Chuẩn ánh xạ quy trình của 15288 (hệ thống) và 12207 (phần mềm) sang tài liệu. Vì vậy từ một bước trong vòng lặp có thể suy ra tài liệu nào bước đó tạo ra. Một bản dự thảo mới cập nhật theo 15288:2023 và 12207:2026; chưa xác nhận bản này đã ban hành chưa **[đã kiểm, trạng thái chưa rõ]**.

**Đề xuất:** dùng 7 loại của 15289 cộng "record" làm trường `type` trong frontmatter của mọi tài liệu. Đây là bộ phân loại trung lập với ngành, nên ở được trong core.

## 3. Lớp B: nội dung từng loại tài liệu

### 3.1. Chuẩn quốc tế (đầy đủ, nặng)

| Tài liệu | Chuẩn | Ghi chú |
| --- | --- | --- |
| Đặc tả yêu cầu (StRS, SyRS, SRS) | ISO/IEC/IEEE 29148 | Đặc tính chất lượng của một yêu cầu và của cả bộ yêu cầu. Đã có nghiên cứu dùng LLM chấm theo 29148 **[đã kiểm]** |
| Mô tả kiến trúc | ISO/IEC/IEEE 42010 | Khái niệm stakeholder, concern, viewpoint, view, correspondence, rationale **[chưa kiểm phiên bản 2022]** |
| Thiết kế phần mềm | IEEE 1016 | Các design viewpoint **[chưa kiểm]** |
| Tài liệu kiểm thử | ISO/IEC/IEEE 29119-3 | Kế hoạch, đặc tả, báo cáo kiểm thử **[chưa kiểm]** |
| Tài liệu người dùng phần mềm | ISO/IEC/IEEE 26514 (họ 26511–26515) | Không tìm thấy công cụ AI nào nhắm riêng chuẩn này **[đã kiểm: không có kết quả]** |
| Hướng dẫn sử dụng sản phẩm (mọi ngành) | IEC/IEEE 82079-1:2019 | Áp dụng cho mọi sản phẩm, kể cả phần cứng. Điều 5 gồm mục đích, chất lượng thông tin và quy trình quản lý thông tin; **tối giản (minimalism)** là điều 5.3.3. Có phụ lục hướng dẫn đánh giá sự phù hợp. Nhiều điều khoản viết ở dạng bắt buộc chứ không chỉ khuyến nghị **[đã kiểm, nguồn thứ cấp]** |
| Quản lý cấu hình | ISO 10007 | Định danh, phiên bản, baseline **[chưa kiểm]** |

### 3.2. Cấu trúc tinh gọn (nhẹ, dễ dùng)

| Cấu trúc | Nội dung | Bằng chứng sử dụng |
| --- | --- | --- |
| **Diátaxis** | 4 loại: tutorial (học), how-to (làm một việc), reference (tra), explanation (hiểu) | Vài trăm dự án dùng; có Canonical/Ubuntu, Gatsby; Python bàn việc áp dụng dần. Canonical cảnh báo: khi mới áp dụng, tài liệu cũ trông tệ hơn vì lỗ hổng lộ ra. Không có nghiên cứu độc lập đo hiệu quả **[đã kiểm]** |
| **Kiểu topic của DITA** | concept ("là gì?"), task ("làm thế nào?"), reference (thông tin định lượng về một thứ cụ thể) | Gốc từ Information Mapping của Robert Horn và kỹ thuật STOP của Hughes Aircraft. Tập kiểu là mở, được thêm kiểu mới **[đã kiểm]** |
| **Information Mapping** | 7 kiểu: procedure, process, concept, structure, classification, principle, fact | **[chưa kiểm danh sách]** |
| **The Good Docs Project** | Mẫu mã nguồn mở: README, tutorial, how-to, concept, reference, troubleshooting (triệu chứng → nguyên nhân → cách xử lý), gom thành các gói mẫu | Chưa có danh sách chính thức gom một chỗ; nên xem repo `gitlab.com/tgdp/templates` **[đã kiểm]** |
| **ADR** | Nygard (ngắn: bối cảnh, quyết định, hệ quả) và MADR (thêm các phương án và ưu nhược) | Một thí nghiệm có đối chứng cho thấy mẫu Nygard được đánh giá tổng thể cao hơn MADR; MADR tốt hơn khi cần chi tiết cấu trúc **[đã kiểm]** |
| **arc42** | 12 mục, tuỳ biến được | Cách rút gọn hay gặp: bắt đầu với mục 1 (mục tiêu), 3 (ngữ cảnh), 4 (chiến lược giải pháp). Dự án quá nhỏ thì chỉ cần README **[đã kiểm, nguồn cộng đồng]** |
| **C4** | 4 mức sơ đồ: context, container, component, code | **[chưa kiểm]** |
| **RAD-AI** | Mở rộng arc42 thêm 8 mục và C4 thêm 3 loại sơ đồ cho hệ có AI, ánh xạ thành viewpoint mới của 42010, kèm EU AI Act Annex IV | Bài báo 3/2026, chưa có bằng chứng áp dụng **[đã kiểm]** |

### 3.3. Ghép hai nhóm lại

Diátaxis và DITA sinh ra cho **tài liệu người dùng**. 15289 bao cả **tài liệu kỹ thuật nội bộ** của vòng đời. Hai nhóm không thay được nhau nhưng khớp với nhau:

| Loại 15289 | Cấu trúc tinh gọn dùng làm mẫu |
| --- | --- |
| specification | EARS + đặc tính 29148, mỗi yêu cầu một dòng có ID |
| description | arc42 rút gọn (mục 1, 3, 4, 5) + sơ đồ C4 |
| policy / quyết định | ADR kiểu Nygard |
| procedure | how-to (Diátaxis) hoặc task (DITA), viết theo tối giản của 82079-1 |
| report | báo cáo kiểm chứng: phạm vi, bằng chứng, phán quyết |
| request | issue / troubleshooting của Good Docs |
| record | không viết tay; sinh từ công cụ |
| (tra cứu) | reference (Diátaxis/DITA): bảng, giá trị, có nguồn |
| (giải thích) | explanation / concept: tuỳ chọn |

## 4. Lớp C: câu chữ

| Chuẩn | Dùng cho | Kiểm tự động |
| --- | --- | --- |
| **INCOSE Guide for Writing Requirements** (v4, khoảng 42 luật) | câu yêu cầu | Có công cụ thương mại (QVscribe, Codebeamer AI, Innoslate) và một công cụ miễn phí trên trình duyệt. Mỗi công cụ phủ một phần luật, ví dụ QVscribe từng được ghi nhận phủ 24/44 luật. Số luật khác nhau theo phiên bản tài liệu **[đã kiểm]** |
| **EARS** | mẫu câu yêu cầu (ubiquitous, event-driven, state-driven, unwanted behaviour, optional) | Dễ kiểm bằng regex **[chưa kiểm chi tiết mẫu]** |
| **ASD-STE100** | tiếng Anh kỹ thuật có từ điển giới hạn | Miễn phí từ Issue 6 (2013). ASD cho biết các công cụ kiểm STE tự động có độ chính xác không đồng đều. Có add-on thử nghiệm cho Oxygen và nhiều agent skill viết theo STE, nhưng chỉ dựa trên prompt **[đã kiểm]** |
| **Tối giản (82079-1, điều 5.3.3)** | hướng dẫn thao tác: hướng vào hành động, người dùng muốn làm xong việc | Chỉ kiểm được một phần (độ dài bước, câu mệnh lệnh) **[đã kiểm, nguồn thứ cấp]** |
| **Style guide** (Microsoft, Google) | văn phong chung | Vale có gói luật cộng đồng cho Microsoft (của errata-ai, không phải Microsoft làm) **[đã kiểm]**; gói Google **[chưa kiểm]** |

Lưu ý cho archwright: tài liệu hiện viết **tiếng Việt, định danh tiếng Anh**. STE và các gói Vale chỉ áp được cho phần tiếng Anh. Phần tiếng Việt cần bộ luật riêng, đơn giản: câu ngắn, mỗi câu một ý, thuật ngữ theo bảng thuật ngữ của dự án, không viết tắt khi chưa định nghĩa.

## 5. Chuẩn riêng theo domain (để trong domain pack)

Tất cả mục dưới đây là **[chưa kiểm]**: tên chuẩn chính xác, nhưng phạm vi và phiên bản cần đối chiếu khi viết từng domain pack.

| Domain pack | Chuẩn tài liệu nên có trong profile |
| --- | --- |
| `embedded-mcu` | IEC 61508 (an toàn chức năng chung), ISO 26262 (ô tô), IEC 62304 (phần mềm y tế); yêu cầu truy vết hai chiều yêu cầu ↔ thiết kế ↔ kiểm thử; MISRA C cho quy tắc mã |
| `pcb-design` | IPC-2612/2611 (tài liệu sơ đồ điện), IPC-2581 (dữ liệu sản xuất), IEC 81346 (mã định danh tham chiếu), IEC 60617 (ký hiệu), IPC-2221 (thiết kế), IPC-A-610 (tiêu chí nghiệm thu lắp ráp) |
| `mechanical-design` | ISO 128 / ISO 129 (bản vẽ, ghi kích thước), ISO 7200 (khung tên), ISO GPS hoặc ASME Y14.5 (dung sai hình học), ISO 10209 (thuật ngữ tài liệu kỹ thuật), ISO 12100 (đánh giá rủi ro máy), AIAG-VDA FMEA, IEC/IEEE 82079-1 cho hướng dẫn sử dụng |
| `llm-agent` | EU AI Act Annex IV (hồ sơ kỹ thuật hệ rủi ro cao, áp dụng từ 2/8/2026 **[đã kiểm]**), ISO/IEC 42001 (hệ quản lý AI), NIST AI RMF, model card / system card, RAD-AI cho arc42 |

## 6. Đề xuất thiết kế cho archwright

### 6.1. Hai trục: `type` và `form`

Bản đầu của mục này đề xuất 6 loại tài liệu cố định. Thử giấy trên hai domain nhúng và cơ khí cho thấy bộ 6 loại chỉ xếp vừa 9/32 tài liệu ([paper-tests/doc-types.md](../paper-tests/doc-types.md)). Nguyên nhân chung: một trường phải làm hai việc, vừa phân loại vừa chọn mẫu. Bản này tách thành hai trục. Thử giấy lần hai, làm độc lập trên `pcb-design` ([paper-tests/doc-types-pcb.md](../paper-tests/doc-types-pcb.md)), không cần thêm giá trị `type` nào; các lỗ hổng tìm được nằm ở `form` và frontmatter, và đã được sửa trong bản này.

- **`type`**: phân loại, dùng để so sánh giữa các domain. Giá trị là đúng 7 loại của 15289 cộng `record`: `description`, `plan`, `policy`, `procedure`, `report`, `request`, `specification`, `record`. Core không tự đặt thêm. Một file gộp nhiều loại thì ghi danh sách.
- **`form`**: mẫu cụ thể, quyết định mục bắt buộc và luật kiểm. Core có vài `form` trung lập với ngành; domain pack thêm `form` của mình.

`form` trong core:

| `form` | `type` | Mục bắt buộc | Ghi chú |
| --- | --- | --- | --- |
| `approval` | record | đối tượng duyệt (id + phiên bản hoặc hash), bằng chứng, kết luận, người duyệt, ngày | Mẫu: [forms/approval.md](forms/approval.md) |
| `baseline` | record | cổng, danh sách artefact và phiên bản, trạng thái kiểm chứng của từng artefact | Mẫu: [forms/baseline.md](forms/baseline.md) |
| `change-request` | request | vấn đề hoặc mong muốn, tiêu chí xong, phạm vi ảnh hưởng | gồm yêu cầu tính năng, ECO |
| `known-failure` | record | triệu chứng, nguyên nhân, cách xử lý, trạng thái | mẫu troubleshooting. Triệu chứng là chuỗi log nguyên văn ở phần mềm; ở phần cứng là số đo hoặc ảnh, đặt trong `evidence` |
| `deviation` | record, request | thứ được miễn, phạm vi, lý do, biện pháp bù, hạn, người duyệt | Mẫu: [forms/deviation.md](forms/deviation.md) |
| `adr` | description | bối cảnh, quyết định, hệ quả, trạng thái | kiểu Nygard |
| `design-note` | description | mục tiêu, ngữ cảnh, phân rã, giao diện | trung lập; arc42/C4 là `form` của domain phần mềm |
| `howto` | procedure | điều kiện trước, các bước đánh số, kết quả mong đợi | tối giản theo 82079-1 |
| `verify-report` | report | phạm vi, bằng chứng, phán quyết | sinh từ `verify.py` |
| `review-report` | report | phương pháp, phát hiện, kết luận phán đoán | do người hoặc agent viết |
| `rules` | policy | danh sách quy tắc có ID và lý do | `CLAUDE.md`, checklist, luật DFM |
| `register` | bất kỳ | một file nhiều mục, mỗi mục có ID | `decisions.md`, `SOURCES.md` |

`form` của domain pack được `extends` một `form` của core và được thay danh sách mục bắt buộc, ví dụ `errata` của `pcb-design` mở rộng `known-failure` thêm "rev bị ảnh hưởng, rev đã sửa".

Ví dụ `form` của domain pack: `ears-spec` (nhúng, phần mềm), `param-spec` (bảng thông số có dung sai, phần cứng), `drawing` (cơ khí, metadata đọc từ khung tên), `sim-report` (FEA: trường hợp tải, điều kiện biên, lưới), `hazard-analysis` (nhúng an toàn).

Frontmatter chung:

```yaml
id: SPEC-012
type: specification                      # 1 hoặc nhiều trong 8 giá trị trên
form: ears-spec
status: draft | reviewed | approved | superseded
origin: authored | generated | external  # generated/external: agent chỉ trỏ tới, không sửa
owner: <người chịu trách nhiệm>
owner_domain: embedded-mcu               # tuỳ chọn
shared_with: [pcb-design]                # tuỳ chọn: tài liệu dùng chung
audience: dev | reviewer | operator | end-user
sources: [refs/soc-datasheet.txt#L120]   # nguyên lý "con số có nguồn"
traces: [D-003, TEST-hil-sleep]          # liên kết truy vết; ma trận truy vết sinh từ trường này
evidence: [photos/t1-drop.jpg]           # tuỳ chọn: file bất kỳ, kể cả ảnh, STEP, mã mẫu vật lý
standard: [ISO/IEC/IEEE 29148]           # chuẩn mà tài liệu tự nhận theo dàn ý
rev: B                                   # tuỳ chọn: phiên bản của chính tài liệu hay artefact
applies_to: [rev-B, variant-lite, SN0007] # tuỳ chọn: rev, biến thể, serial hoặc lô mà nội dung áp dụng
as_of: 2026-10-29                        # tuỳ chọn: ngày của dữ liệu đổi theo thời gian (giá, tồn kho, báo giá)
derived_from: [pcb-layout@rev-B]         # tuỳ chọn: tài liệu này sinh ra từ đâu, kèm phiên bản
manual_edits: [alternates, dnp]          # tuỳ chọn, chỉ khi origin = generated: phần được sửa tay sau khi sinh
```

Quy tắc cho các trường mới:

- `derived_from` cho phép `doclint` phát hiện đầu ra cũ hơn nguồn, ví dụ Gerber sinh từ layout rev A trong khi layout đã ở rev B.
- Tài liệu sinh ra rồi sửa tay (BOM thêm linh kiện thay thế, pin map thêm tên tín hiệu) ghi `origin = generated` và liệt kê phần sửa tay trong `manual_edits`. Agent chỉ được sửa các phần đó; phần còn lại phải sinh lại từ nguồn.
- Tài liệu có `shared_with` thì mỗi thay đổi cần bản ghi `approval` có người duyệt thuộc `owner_domain` và thuộc từng domain trong `shared_with` (luật 7 của [approval](forms/approval.md)).
- Nguồn tri thức chỉ tra lúc dùng (tồn kho, giá trực tuyến, `access = "query"` trong [core-model.md §5](../core-model.md#5-mô-tả-bằng-file)) không lưu thành file thì không phải tài liệu, không cần frontmatter.

File không phải Markdown (bản vẽ, bảng tính, mô hình CAD, bộ Gerber) khai metadata theo một trong ba cách, chọn trong profile:

- `meta_from = "sidecar"`: file đi kèm `<file>.meta.toml`.
- `meta_from = "manifest"`: một file TOML khai metadata cho nhiều file, ví dụ cho cả thư mục datasheet. Tránh phải viết hàng trăm sidecar.
- `meta_from = "title-block"` (hoặc thuộc tính khác của file): đọc từ chính file, kèm bảng `meta_map` ánh xạ ô của khung tên sang trường frontmatter.

`unit = "set"` cho biết cả tập file khớp `files` là **một** tài liệu (bộ Gerber + drill, schematic phân cấp); mặc định `unit = "file"`, mỗi file một tài liệu. `doclint` chỉ kiểm metadata của các file này, không kiểm nội dung.

### 6.2. Doc profile trong domain pack

Viết bằng cùng cú pháp TOML của [core-model.md §5](../core-model.md#5-mô-tả-bằng-file), mọi mục đều tuỳ chọn:

```toml
[[doc_form]]
id = "ears-spec"
type = "specification"
template = "forms/ears-spec.md"
required_sections = ["Yêu cầu", "Cách kiểm chứng"]
lint = ["ears", "incose-core", "number-has-source"]

[[doc_form]]
id = "hazard-analysis"            # form riêng của domain nhúng an toàn
type = "report"
extends = "review-report"
standard = ["IEC 61508"]
required_sections = ["Mối nguy", "Mức SIL", "Biện pháp", "Truy vết tới yêu cầu"]

[[doc_form]]
id = "drawing"
type = "specification"
files = ["cad/**/*.pdf"]
meta_from = "title-block"
meta_map = { "Rev" = "rev", "Drawing No." = "id", "Date" = "as_of" }

[[doc_form]]
id = "fab-package"               # form riêng của pcb-design
type = "specification"
files = ["fab/gerber/*"]
unit = "set"                      # cả bộ Gerber + drill là một tài liệu
meta_from = "manifest"
required_fields = ["rev", "derived_from"]

[[step]]
id = "doclint";  kind = "check";  speed = "fast"
when = { paths = ["docs/**"] }
evidence = { type = "binary" }
```

### 6.3. Kiểm chứng: cái gì máy chấm, cái gì người chấm

| Kiểm | Dạng bằng chứng | Công cụ |
| --- | --- | --- |
| Đủ frontmatter, đủ mục bắt buộc | nhị phân | script trong `doclint` |
| Con số không có nguồn | nhị phân | regex số + kiểm trường `sources` (đã có ý tưởng tương tự cho `decisions.md` ở [architecture.md §7](../architecture.md#7-brainstorm-ý-tưởng-mở-rộng-chưa-hiện-thực)) |
| Liên kết truy vết còn sống, không có yêu cầu mồ côi | nhị phân | script; hoặc StrictDoc / Sphinx-needs **[chưa kiểm]** |
| Câu yêu cầu theo EARS, tránh từ mơ hồ ("nhanh", "phù hợp", "khoảng") | chỉ số (tỉ lệ vi phạm ≤ ngưỡng) | Vale với bộ luật riêng |
| Văn phong tiếng Anh theo STE hoặc style guide | chỉ số | Vale |
| Nội dung đúng kỹ thuật, đủ với stakeholder | phán đoán | `reviewer` theo checklist của domain pack; người duyệt kết luận |

Theo nguyên lý của core: nếu bước phán đoán chưa chạy thì tài liệu ở trạng thái `reviewed` cùng lắm là BLOCKED, không bao giờ `approved`.

### 6.4. Lộ trình gợi ý

1. ~~Thử giấy trên domain nhúng và cơ khí~~: đã làm, xem [paper-tests/doc-types.md](../paper-tests/doc-types.md). Thử lần hai trên `pcb-design`: đã làm, xem [paper-tests/doc-types-pcb.md](../paper-tests/doc-types-pcb.md).
2. Viết các `form` của core (đã có nháp [approval](forms/approval.md), [baseline](forms/baseline.md) và [deviation](forms/deviation.md)) và skill `doc-standard`. Đo bằng eval: cho agent viết 5 tài liệu có và không có skill, chấm theo `doclint` và rubric.
3. ~~Viết `doclint` bản nhỏ nhất~~: đã có [kit/core/tools/doclint.py](../../kit/core/tools/doclint.py) (frontmatter, type/form/status, trường và mục bắt buộc, luật của `approval` / `baseline` / `deviation`, liên kết và anchor, cảnh báo con số không nguồn, phán quyết của báo cáo làm bằng chứng, người duyệt theo domain qua bảng `[people]`, bảng artefact của `baseline` so với `artefacts` / `[gates]` của profile, `derived_from` cũ hơn nguồn, file không phải Markdown qua sidecar hoặc manifest, `unit = "set"`). Chưa làm: đọc khung tên bản vẽ (`meta_from = "title-block"` hiện trả BLOCKED), trạng thái theo từng mục trong `register`, hết hạn tự động của `deviation`, và việc bước kiểm đọc `deviation` để bỏ qua vi phạm.
4. Thêm Vale và luật EARS khi đã có ít nhất một domain cần đặc tả yêu cầu nghiêm ngặt.
5. Profile theo ngành (bảng §5) chỉ viết khi có dự án thật của ngành đó.

### 6.5. Rủi ro

- **Bản quyền:** không đưa toàn văn chuẩn ISO/IEC/IEEE vào `refs/`. Chỉ ghi tên chuẩn và tên điều khoản, hoặc dùng bản tổ chức đã mua theo đúng giấy phép. ASD-STE100 là ngoại lệ vì miễn phí.
- **Mẫu quá nặng:** chính các nguồn về arc42 và Diátaxis đều khuyên áp dụng dần. Mẫu dài thì agent điền chữ cho đủ chỗ, tạo nội dung rỗng.
- **Tự nhận tuân thủ:** trường `standard` chỉ là "tài liệu viết theo dàn ý của chuẩn X", không phải chứng nhận phù hợp. Đánh giá phù hợp thật (ví dụ theo phụ lục của 82079-1) là việc của người.
- **LLM bịa nội dung:** chưa thấy nghiên cứu nào đo riêng agent viết tài liệu theo mẫu chuẩn. Các nghiên cứu gần nhất về truy vết nguồn gốc của agent và về ảo giác khi sinh sơ đồ UML đều ủng hộ cùng một hướng: buộc mỗi khẳng định trỏ về nguồn **[đã kiểm]**.

## 7. Câu hỏi còn mở

Từ thử giấy trên `pcb-design` ([paper-tests/doc-types-pcb.md](../paper-tests/doc-types-pcb.md) §5.3):

- **Trạng thái theo từng mục trong `register`** (P11): ví dụ thư viện footprint, mục nào đã kiểm, errata nào đã sửa ở rev nào. Có cho mỗi mục một `status` riêng không, hay tách thành nhiều file?
- **Lý do cho luật máy đọc** (P13): file luật DRC hay net class có tên luật mà không có chỗ ghi lý do. Có cần một `rules` dạng Markdown song song không?
- **Ranh giới artefact và tài liệu** (P15): schematic và layout vừa là artefact vừa là tài liệu. Vòng đời `draft → reviewed → approved` của tài liệu có trùng với `baseline` + `approval` không, và `doclint` có kiểm chúng không?
- **Bản thể vật lý** (P7): `applies_to` ghi được serial và lô, nhưng chưa rõ serial có cần thành một khái niệm trong core-model không.

Câu hỏi từ trước:

- Tài liệu viết cho khách hàng (hướng dẫn sử dụng theo 82079-1) có thuộc phạm vi archwright không, hay chỉ tài liệu kỹ thuật nội bộ?
- Ngôn ngữ chính của tài liệu dự án: chỉ tiếng Việt, chỉ tiếng Anh, hay song ngữ? Câu trả lời quyết định có dùng STE hay không.
- Có ngành nào sắp làm bắt buộc theo chuẩn an toàn (61508, 26262, 62304) không? Nếu có, truy vết hai chiều nên vào core sớm hơn.

## Nguồn

- ISO/IEC/IEEE 15289: [IEEE SA 2019](https://standards.ieee.org/ieee/15289/7196/), [bản dự thảo mới](https://standards.ieee.org/ieee/15289/11891/), [ISO OBP 2015](https://www.iso.org/obp/ui/#iso:std:iso-iec-ieee:15289:ed-2:v1:en), [IEC Webstore](https://webstore.iec.ch/en/publication/65566), [trích mẫu 2017](https://cdn.standards.iteh.ai/samples/71950/7d7ac44e727045de8bddfc9f46d6350e/ISO-IEC-IEEE-15289-2017.pdf)
- IEC/IEEE 82079-1: [tcworld](https://www.tcworld.info/e-magazine/technical-writing/information-for-use-of-products-1066), [INSTRKTIV](https://instrktiv.com/en/82079/), [VDE preview](https://www.vde-verlag.de/iec-normen/preview-pdf/info_iecieee82079-1{ed2.0}b.pdf), [EVS](https://www.evs.ee/en/iec-ieee-82079-1-2019)
- Diátaxis: [Canonical](https://ubuntu.com/blog/diataxis-a-new-foundation-for-canonical-documentation), [Python discuss](https://discuss.python.org/t/adopting-the-diataxis-framework-for-python-documentation/15072), [diataxis.fr](https://www.diataxis.fr/colophon/)
- DITA và Information Mapping: [OASIS DITA 1.3 information typing](https://docs.oasis-open.org/dita/dita/v1.3/cos02/part1-base/archSpec/base/information-typing.html), [OASIS DITA 1.2](https://docs.oasis-open.org/dita/v1.2/os/spec/archSpec/dita_technicalContent_InformationTypes.html), [Medallia style guide](https://docs.medallia.com/medallia-documentation/medallia-product-documentation-style-guide/information-mapping)
- The Good Docs Project: [release Capilano](https://tgdp-www.netlify.app/blog/release-capilano), [release Dragon](https://tgdp-www.netlify.app/blog/release-dragon), [troubleshooting template](https://tgdp-www.netlify.app/template/troubleshooting)
- ADR và arc42: [so sánh mẫu ADR](https://fugumt.com/fugumt/paper_check/2604.27333v1), [joelparkerhenderson/architecture-decision-record](https://hn.jakechampion.name/reader/https://github.com/joelparkerhenderson/architecture-decision-record), [arc42 skill](https://skills.sh/oocx/tfplan2md/arc42-documentation), [arc42 + C4 skill](https://www.skills.sh/marvinrichter/clarc/arc42-c4)
- RAD-AI và C4 cho agentic AI: [arXiv 2603.28735](https://arxiv.org/pdf/2603.28735), [arXiv 2603.15021](https://arxiv.org/html/2603.15021v1)
- Yêu cầu (INCOSE, 29148): [QRA](https://qracorp.com/guides_checklists/automating-the-incose-guide-for-writing-requirements/), [NLP4RE 2020](https://ceur-ws.org/Vol-2584/NLP4RE-paper3.pdf), [PTC Codebeamer](https://support.ptc.com/help/codebeamer_ai/en/codebeamer/requirement_assistant/ra_intro.html), [Innoslate](https://specinnovations.com/blog/meet-incoses-guide-to-writing-requirements-with-ai-quality-checker-webinar), [INCOSE Requirements Workbench](https://ssaleem74.github.io/incose-requirements-workbench/), [arXiv 2408.10886](https://ar5iv.labs.arxiv.org/html/2408.10886), [ARQM](https://www.researchsquare.com/article/rs-7743410), [INCOSE MBSE25](https://www.incose.org/wp-content/uploads/2026/07/MBSE25-Final-Paper-28-with-Cover-Page.pdf)
- STE và style guide: [ASD white paper](https://www.asd-ste100.org/assets/files/WhitePaper-ASD-STE100_and_AI.pdf), [ASD FAQ](https://www.asd-europe.org/standards-specifications/simplified-technical-english/faq-simplified-technical-english-ste/), [Oxygen STE add-on](https://www.oxygenxml.com/addons/oxygen-terminology-checker-asd-ste100-styleguide.html), [Oxygen/errata-ai](https://mailman.oxygenxml.com/hyperkitty/list/oxygen-user@oxygenxml.com/thread/ZZV43L7NITWACXN6EDINMCCWULOERTF3/), [PostHog STE skill](https://skills.sh/posthog/ai-plugin/writing-simplified-technical-english)
- LLM, ảo giác và truy vết: [arXiv 2606.04990](https://arxiv.org/html/2606.04990), [arXiv 2610.30946](https://arxiv.org/abs/2610.30946), [arXiv 2605.01562](https://arxiv.org/pdf/2605.01562), [AgentHallu](https://aclanthology.org/2026.emnlp-main.925/), [CMES 2026](https://www.sciencedirect.com/org/science/article/pii/S1526149226001906)
