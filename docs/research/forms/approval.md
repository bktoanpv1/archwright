---
id: FORM-APPROVAL
type: specification
form: form-spec
status: draft
origin: authored
---

# Form `approval`: bản ghi duyệt

Trạng thái: nháp, chưa dùng thật. Khi có `kit/core`, file này chuyển thành mẫu của core.

Giải quyết lỗ hổng G4 trong [paper-tests/doc-types.md](../../paper-tests/doc-types.md): mọi cổng duyệt (duyệt thiết kế, duyệt merge, duyệt kiểu dáng, chốt thiết kế) cần ghi lại **ai đã duyệt cái gì, dựa trên bằng chứng nào**. ADR quá nặng cho việc này. Đây là bản ghi của nguyên lý 3 trong [core-model.md §4](../../core-model.md#4-thứ-bất-biến-duy-nhất-nguyên-lý-không-phải-cấu-trúc): người giữ quyền quyết.

## Khi nào dùng

- Mỗi lần một bước loại `decide` kết thúc, kể cả khi kết luận là từ chối.
- Không dùng để giải thích *vì sao* chọn một hướng thiết kế. Việc đó là của `adr`; bản ghi duyệt chỉ trỏ tới ADR.

## Trường

| Trường | Bắt buộc | Nội dung |
| --- | --- | --- |
| `id` | có | `APR-<số>` |
| `type` | có | luôn là `record` |
| `form` | có | luôn là `approval` |
| `gate` | có | id của bước `decide` trong mô tả dự án, ví dụ `merge`, `design-review`, `design-freeze` |
| `subject` | có | thứ được duyệt: id artefact hoặc tài liệu **kèm phiên bản bất biến** (git hash, tag, mã revision, id phiên bản ở hệ thống ngoài). Không chấp nhận "bản mới nhất" |
| `evidence` | có | danh sách báo cáo làm căn cứ (`verify-report`, `review-report`, ảnh, mẫu vật lý). Được rỗng chỉ khi `verdict` là `rejected` hoặc `deferred` |
| `verdict` | có | `approved`, `approved-with-conditions`, `rejected`, `deferred` |
| `conditions` | khi `approved-with-conditions` | điều kiện, mỗi điều kiện có hạn hoặc mốc kiểm |
| `accepted_risks` | khi có bằng chứng BLOCKED hoặc FAIL | bằng chứng nào chưa có hoặc chưa đạt, và người duyệt chấp nhận rủi ro gì |
| `approver` | có | **người**, không phải agent. Có thể nhiều người |
| `date` | có | ngày duyệt, dạng `YYYY-MM-DD` |
| `origin` | có | `authored` khi ghi tay; `generated` khi sinh từ lượt approve của PR |
| `traces` | không | ADR, change request, baseline liên quan |

## Luật cho `doclint`

Tất cả là kiểm nhị phân:

1. Đủ trường bắt buộc; `verdict` thuộc 4 giá trị cho phép.
2. `subject` có phiên bản bất biến (khớp mẫu hash, tag hoặc revision mà profile khai báo).
3. Mọi đường dẫn trong `evidence` tồn tại.
4. Nếu một báo cáo trong `evidence` có phán quyết BLOCKED hoặc FAIL mà `verdict` là `approved` hay `approved-with-conditions`, thì `accepted_risks` phải có nội dung. Đây là cách ghi lại quy tắc "BLOCKED không bao giờ ghi thành PASS": người duyệt vẫn được cho qua, nhưng phải ghi rõ mình nhận rủi ro gì.
5. `approver` không phải tên một vai trò agent (`builder`, `reviewer`, `verifier`, `curator`, `planner` hoặc vai trò agent mà dự án khai báo).
6. Bản ghi đã có `verdict` thì không sửa. Duyệt lại thì tạo bản ghi mới, ghi bản cũ vào `traces`.
7. Nếu `subject` là tài liệu có `shared_with`, thì `approver` phải có ít nhất một người của `owner_domain` và một người của mỗi domain trong `shared_with`. Profile của dự án khai người nào thuộc domain nào. Ví dụ: pin map do `pcb-design` sở hữu, dùng chung với `embedded-mcu`, nên cần người duyệt của cả hai bên.

Không kiểm được: người duyệt đã thật sự đọc bằng chứng hay chưa. Đó là trách nhiệm của người duyệt.

## Dạng lưu

- **Mỗi lần duyệt một file**, `docs/approvals/APR-<số>.md`, khi bản ghi có nhiều điều kiện hoặc rủi ro.
- **Sổ** (`form = register`), `docs/approvals.md`, mỗi lần duyệt một mục, khi phần lớn các lần duyệt đơn giản. Đây là dạng nên dùng mặc định.
- **Sinh từ PR**: khi dự án duyệt merge trên GitHub hoặc GitLab, lượt approve đã là bản ghi. Một script có thể chép nó vào sổ với `origin = generated`, để mọi cổng duyệt nằm cùng một chỗ.

## Mẫu: một file

```markdown
---
id: APR-<số>
type: record
form: approval
gate: <id bước decide>
subject: <id artefact>@<phiên bản bất biến>
evidence:
  - <đường dẫn báo cáo>
verdict: approved | approved-with-conditions | rejected | deferred
conditions: []
accepted_risks: []
approver: [<người>]
date: YYYY-MM-DD
origin: authored
traces: []
---

# APR-<số>: <gate> cho <subject>

<Một hoặc hai câu: duyệt gì, kết luận gì. Chỉ viết thêm khi có điều kiện, rủi ro hoặc lý do từ chối.>
```

## Mẫu: một mục trong sổ

```markdown
## APR-<số> · <gate> · <subject>@<phiên bản> · <verdict>

- Bằng chứng: <đường dẫn>, <đường dẫn>
- Rủi ro nhận: <nếu có>
- Điều kiện: <nếu có>
- Người duyệt: <người> · <YYYY-MM-DD>
```

## Ví dụ (DEMO)

Duyệt merge firmware khi bench HIL bận. Domain nhúng, dự án minh hoạ `soil-node` ở [architecture.md §8](../../architecture.md#8-demo-dự-án-nhúng-examplessoil-node):

```markdown
## APR-007 · merge · firmware@a1b2c3d · approved-with-conditions

- Bằng chứng: reports/verify-a1b2c3d.md (build, host test, bộ nhớ: PASS; HIL: BLOCKED vì bench bận)
- Rủi ro nhận: dòng ngủ sâu chưa đo trên bench sau khi đổi driver ADC
- Điều kiện: chạy HIL trước đợt OTA đầu tiên; nếu FAIL thì không phát hành
- Người duyệt: <kỹ sư senior> · 2026-10-29
```

Chốt thiết kế vỏ trước khi làm khuôn. Domain cơ khí; `subject` trỏ tới một baseline thay vì từng file:

```markdown
## APR-012 · design-freeze · BL-003 · approved-with-conditions

- Bằng chứng: reports/geo-check-BL-003.md, reports/print-fit-03.md (ảnh lắp thử), reports/review-dfm-03.md (BLOCKED: chờ nhà làm khuôn xác nhận góc thoát)
- Rủi ro nhận: nếu góc thoát không đủ thì phải sửa khuôn bớt thép sau T1
- Điều kiện: nhà làm khuôn xác nhận góc thoát trước khi cắt thép
- Người duyệt: <trưởng thiết kế>, <đại diện nhà làm khuôn> · 2026-10-29
```
