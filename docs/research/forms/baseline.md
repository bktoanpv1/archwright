---
id: FORM-BASELINE
type: specification
form: form-spec
status: draft
origin: authored
---

# Form `baseline`: tập artefact và phiên bản tại một cổng

Trạng thái: nháp, chưa dùng thật. Khi có `kit/core`, file này chuyển thành mẫu của core.

Giải quyết lỗ hổng G14 trong [paper-tests/doc-types.md](../../paper-tests/doc-types.md). Ở một số cổng, thứ được duyệt hay phát hành không phải một file mà là **một tập artefact ở các phiên bản cụ thể**, ví dụ: firmware trên một đợt OTA, bộ CAD + bản vẽ + BOM khi chốt thiết kế, bộ file gửi nhà sản xuất mạch. Baseline ghi lại tập đó để trả lời được hai câu sau này: "đợt này chạy đúng những gì?" và "từ lần trước đã đổi gì?". Khái niệm lấy từ quản lý cấu hình (ISO 10007 **[chưa kiểm]**).

## Khi nào dùng

- Ngay trước một bước `decide` duyệt cả một tập (chốt thiết kế, phát hành). Bản ghi `approval` khi đó có `subject` là id của baseline.
- Mỗi lần một bước `release` đưa thứ gì ra ngoài repo: thiết bị, nhà sản xuất, khách hàng.
- Không dùng cho mỗi commit; git đã làm việc đó.

## Trường

| Trường | Bắt buộc | Nội dung |
| --- | --- | --- |
| `id` | có | `BL-<số>` |
| `type` | có | luôn là `record` |
| `form` | có | luôn là `baseline` |
| `gate` | có | id bước `decide` hoặc `release` mà baseline phục vụ |
| `previous` | không | id baseline trước, để tính thay đổi |
| `items` | có | danh sách artefact, xem bảng dưới |
| `status` | có | `proposed` → `frozen` (đã có `approval`) → `superseded` |
| `approval` | khi `frozen` | id bản ghi `approval` |
| `date` | có | ngày lập |
| `origin` | có | nên là `generated`: script đọc phiên bản từ git và từ hệ thống ngoài |

Mỗi mục trong `items`:

| Trường | Bắt buộc | Nội dung |
| --- | --- | --- |
| `artefact` | có | id artefact trong mô tả dự án ([core-model.md §5](../../core-model.md#5-mô-tả-bằng-file)) |
| `version` | có | phiên bản bất biến: git hash, tag, mã revision (rev B), id phiên bản ở hệ thống ngoài, hash sha256 của file nhị phân |
| `verdict` | có | PASS / FAIL / BLOCKED của artefact ở phiên bản này, kèm đường dẫn báo cáo |
| `revert` | khi `store = external` | cách quay về phiên bản trước (lấy từ thuộc tính `revert` của artefact) |
| `change` | khi có `previous` | đổi gì so với baseline trước: một dòng, hoặc id change request |

## Luật cho `doclint`

1. Đủ trường bắt buộc; mọi `version` là định danh bất biến, không phải `latest`, `main` hay tên nhánh.
2. Mọi `artefact` có trong mô tả dự án. Nếu profile khai báo cổng này cần những artefact nào, thì không thiếu artefact nào.
3. Mọi đường dẫn báo cáo trong `verdict` tồn tại, và phán quyết ghi trong baseline khớp phán quyết trong báo cáo.
4. Baseline `frozen` thì không sửa nữa. Muốn đổi thì lập baseline mới với `previous` trỏ về bản cũ, rồi đánh dấu bản cũ `superseded`.
5. Baseline `frozen` có mục FAIL hoặc BLOCKED thì bản ghi `approval` của nó phải có `accepted_risks` (luật 4 của [approval](approval.md)).

## Mẫu

```markdown
---
id: BL-<số>
type: record
form: baseline
gate: <id bước>
previous: BL-<số trước>
status: proposed
approval:
date: YYYY-MM-DD
origin: generated
---

# BL-<số>: <gate>

| Artefact | Phiên bản | Kiểm chứng | Đổi so với BL-<số trước> |
| --- | --- | --- | --- |
| <id> | <phiên bản bất biến> | PASS · <đường dẫn báo cáo> | <một dòng hoặc CR-<số>> |

<Nếu có artefact ở hệ thống ngoài: một dòng cho mỗi artefact về cách quay về bản trước.>
```

Bảng nằm trong thân tài liệu thay vì trong frontmatter để người đọc được. Script sinh baseline viết bảng; `doclint` đọc lại bảng.

## Ví dụ (DEMO)

Phát hành OTA đợt 1, domain nhúng:

```markdown
# BL-004: ota-canary

| Artefact | Phiên bản | Kiểm chứng | Đổi so với BL-003 |
| --- | --- | --- | --- |
| firmware | v0.3.0 (a1b2c3d) | PASS · reports/verify-a1b2c3d.md | driver ADC mới, CR-011 |
| device-config | cfg-v12 (ở server cấu hình) | PASS · reports/config-lint-12.md | không đổi |

device-config: quay về bằng cách đẩy lại cfg-v11.
```

Chốt thiết kế trước khi làm khuôn, domain cơ khí. Hình học được ghi bằng file STEP xuất ra (có hash), vì file CAD gốc có thể là nhị phân:

```markdown
# BL-003: design-freeze

| Artefact | Phiên bản | Kiểm chứng | Đổi so với BL-002 |
| --- | --- | --- | --- |
| housing-cad | rev C (git 9f8e7d6) | PASS · reports/geo-check-BL-003.md | thêm gân trụ vít, CR-020 |
| housing-step | sha256:<hash> | PASS · reports/geo-check-BL-003.md | xuất lại từ rev C |
| drawings | rev C | BLOCKED · reports/review-dfm-03.md | chờ nhà làm khuôn xác nhận góc thoát |
| bom-mech | rev C | PASS · reports/bom-check-03.md | đổi vít M2 → M2.5 |
```

Baseline này có một mục BLOCKED. Theo luật 5, muốn chốt thì `approval` phải ghi rõ người duyệt nhận rủi ro gì.
