---
id: FORM-DEVIATION
type: specification
form: form-spec
status: draft
origin: authored
---

# Form `deviation`: miễn trừ có phạm vi và có hạn

Trạng thái: nháp, chưa dùng thật. Khi có `kit/core`, file này chuyển thành mẫu của core.

Giải quyết lỗ hổng P9 trong [paper-tests/doc-types-pcb.md](../../paper-tests/doc-types-pcb.md). Có lúc dự án cố ý không làm đúng một luật hay một yêu cầu: bỏ qua một vi phạm DRC đã biết là vô hại, thay linh kiện tạm cho một lô vì hết hàng, giữ một cảnh báo MISRA vì driver của hãng, chấp nhận góc thoát khuôn nhỏ hơn luật DFM. Nếu không ghi lại, lần kiểm sau sẽ báo lại cùng vi phạm, hoặc tệ hơn, ai đó tắt luật đi cho cả dự án. Bản ghi miễn trừ cho phép **miễn đúng một chỗ, trong một phạm vi, đến một hạn**.

Trong ngôn ngữ ngành, khái niệm này có nhiều tên: deviation, waiver, concession. Core dùng một tên; domain pack muốn phân biệt (miễn trước khi làm và chấp nhận sau khi đã lỡ làm) thì khai `form` mở rộng.

## Khi nào dùng

- Một luật trong `rules`, một yêu cầu trong `specification`, hay một bước kiểm trong `verify.toml` cho ra vi phạm mà nhóm quyết định chấp nhận.
- Không dùng để đổi luật hay yêu cầu cho mọi trường hợp về sau. Việc đó là sửa chính luật hay yêu cầu, qua `change-request`.
- Không dùng thay cho `accepted_risks` trong `approval`. Bản ghi duyệt nhận rủi ro cho **một lần duyệt**; miễn trừ áp dụng cho mọi lần kiểm trong phạm vi và thời hạn của nó.

## Trường

| Trường | Bắt buộc | Nội dung |
| --- | --- | --- |
| `id` | có | `DEV-<số>` |
| `type` | có | `[record, request]` |
| `form` | có | `deviation` |
| `waives` | có | luật, yêu cầu hay bước kiểm bị miễn: id luật (`DFM-07`), id yêu cầu (`SPEC-012`), hoặc id bước kèm tên vi phạm (`drc:clearance`) |
| `scope` | có | miễn ở đâu, càng hẹp càng tốt: đường dẫn, net, ref designator, tên hàm, tên chi tiết cơ khí |
| `applies_to` | có | rev, biến thể, lô hoặc serial được miễn. Không được để trống, vì miễn cho "mọi rev" thì thực chất là đổi luật |
| `reason` | có | vì sao vi phạm này chấp nhận được |
| `mitigation` | không | biện pháp bù, ví dụ kiểm thêm bằng tay, giới hạn vận hành |
| `expires` | có | ngày hết hạn, hoặc một sự kiện cụ thể (`rev-C`, `lô-3`). Không chấp nhận "vô thời hạn" |
| `status` | có | `requested` → `granted` hoặc `refused` → `expired` hoặc `closed` |
| `approval` | khi `granted` | id bản ghi `approval` |
| `evidence` | không | báo cáo cho thấy vi phạm vô hại, ví dụ số đo hay mô phỏng |
| `traces` | không | change request sẽ sửa tận gốc, known-failure liên quan |

## Luật cho `doclint` và bước kiểm

1. Đủ trường bắt buộc. `applies_to` và `expires` không trống và không mang nghĩa "tất cả".
2. Miễn trừ `granted` phải có `approval`, và người duyệt là người (luật 5 của [approval](approval.md)).
3. Bước kiểm (`verify.py`, DRC, linter) đọc các miễn trừ `granted` còn hạn và **chỉ** bỏ qua vi phạm khớp cả `waives`, `scope` lẫn `applies_to`. Vi phạm cùng loại ở chỗ khác vẫn báo FAIL.
4. Báo cáo của bước kiểm liệt kê các vi phạm đã được miễn kèm id miễn trừ, không giấu chúng. Người đọc báo cáo phải thấy được có bao nhiêu chỗ đang được miễn.
5. Khi hết hạn (đến ngày, hoặc baseline mới có rev hay lô trong `expires`), `doclint` đánh dấu miễn trừ `expired` và bước kiểm báo lại vi phạm.

## Mẫu

```markdown
---
id: DEV-<số>
type: [record, request]
form: deviation
waives: <id luật / yêu cầu / bước:vi phạm>
scope: <chỗ được miễn>
applies_to: [<rev / biến thể / lô / serial>]
expires: <YYYY-MM-DD hoặc sự kiện>
status: requested
approval:
evidence: []
traces: []
---

# DEV-<số>: miễn <waives> tại <scope>

**Lý do:** <vì sao chấp nhận được>

**Biện pháp bù:** <nếu có>
```

Khi một dự án có nhiều miễn trừ ngắn, dùng sổ `docs/deviations.md` (`form = register`), mỗi miễn trừ một mục.

## Ví dụ (DEMO)

Domain `pcb-design`: khe hở nhỏ hơn luật ở chân một linh kiện, đúng theo footprint của hãng:

```markdown
## DEV-003 · drc:clearance · U4 pad 1–2 · rev-B · granted

- Lý do: footprint khuyến nghị trong datasheet của hãng có khe hở 0,15 mm, nhỏ hơn luật 0,2 mm của dự án; nhà sản xuất mạch xác nhận làm được (refs/fab-capability.txt)
- Hết hạn: rev-C (đổi sang gói linh kiện lớn hơn, CR-031)
- Duyệt: APR-021
```

Domain `pcb-design`: thay linh kiện tạm cho một lô vì hết hàng:

```markdown
## DEV-004 · BOM C12 · lô-2 · granted

- Thay: tụ X7R 10 µF 0805 hãng A bằng mã tương đương của hãng B, cùng điện áp và dung sai
- Biện pháp bù: đo ripple nguồn 3,3 V trên 3 board đầu của lô (reports/bringup-lot2.md)
- Hết hạn: lô-3
- Duyệt: APR-022 (người duyệt của pcb-design và embedded-mcu, vì nguồn 3,3 V nằm trong power tree dùng chung)
```
