---
id: ARCH
type: description
form: design-note
status: draft
origin: authored
---

# Kiến trúc archwright: hệ thống khởi tạo dự án

Tổng quan dự án: [README](../README.md). Tài liệu này là thiết kế; `kit/` mới có công cụ đầu tiên là [kit/core/tools/doclint.py](../kit/core/tools/doclint.py), phần còn lại của `kit/` và `examples/` mô tả dưới đây chưa có trong workspace. Bộ khái niệm chung để mô tả mọi dự án (không bắt dự án nào có phần nào giống nhau) nằm ở [core-model.md](core-model.md).

## 1. Ý tưởng cốt lõi

Mọi dự án, ở mọi lĩnh vực, đều cần 5 chức năng:

| Chức năng | Câu hỏi | Hiện thực trong archwright |
| --- | --- | --- |
| **Nguồn gốc** | Thông tin chính xác ở đâu? | `refs/*.txt` (trích xuất nguyên văn, tra bằng `rg`) + `refs/SOURCES.md` |
| **Nhật ký tri thức** | Đã quyết gì, đã học gì? | `docs/decisions.md`, `docs/issues/` |
| **Bản đồ** | Agent và người mới đọc gì trước? | `CLAUDE.md` (≤ 150 dòng, chỉ trỏ đi nơi khác) |
| **Kiểm chứng** | Làm sao biết là đúng? | `tools/verify.py` + `tools/verify.toml` → PASS/FAIL/BLOCKED |
| **Chưng cất** | Biến trải nghiệm thành quy tắc dùng lại được bằng cách nào? | agent `curator`, book-to-skill, `docs/evals.md`, promotion lên domain pack |

Sơ đồ của các domain (`domains/<domain>/`, build bằng `.archify/`) nhóm cùng nội dung này thành **4 khối**:

| Chức năng | Khối trong sơ đồ domain |
| --- | --- |
| Nguồn gốc | Khối 1 · Tri thức (nguồn cần chính xác, `refs/*.txt`) |
| Nhật ký tri thức | Khối 1 · Tri thức (tri thức nội bộ: decisions, issues, evals) |
| Bản đồ | Khối 2 · Agent & công cụ (`CLAUDE.md` là điểm vào của agent) |
| Kiểm chứng | Khối 3 · Workflow (cổng chất lượng tự động, cổng người duyệt) và Khối 4 · Mô hình hoá domain (vòng kiểm chứng của ngành) |
| Chưng cất | Khối 1 · Tri thức (book-to-skill) và Khối 3 · Workflow (`curator` ghi bài học) |

## 2. Ba tầng

```text
┌──────────────────────────────────────────────────────────────┐
│ Tầng 1 · CORE (kit/core)          giống nhau cho mọi lĩnh vực │
│  CLAUDE.md.tmpl · 4 agent · mẫu decisions/issues/evals        │
│  verify.py (runner chung) · checklist chung · SOURCES.md      │
└───────────────────────────┬──────────────────────────────────┘
                            │ overlay (file cùng đường dẫn thì đè)
┌───────────────────────────▼──────────────────────────────────┐
│ Tầng 2 · DOMAIN PACK (domains/<domain>)      mỗi lĩnh vực một │
│  domain.toml: 4 trục chẩn đoán, chế độ trích xuất, quy tắc    │
│               điều hướng chèn vào CLAUDE.md                   │
│  overlay/: checklist chuyên ngành · verify.toml · eval seed · │
│            gợi ý nguồn tài liệu                               │
└───────────────────────────┬──────────────────────────────────┘
                            │ new_project.py (sinh + ghi project.toml)
┌───────────────────────────▼──────────────────────────────────┐
│ Tầng 3 · PROJECT INSTANCE (mỗi dự án một repo git)            │
│  refs/ · docs/ · .claude/{agents,skills} · tools/ · mã nguồn  │
└───────────────────────────┬──────────────────────────────────┘
                            │ promotion: bài học đã kiểm chứng
                            └──────────► quay lại Tầng 2 (người duyệt)
```

- **Core** thay đổi rất ít. Một cải tiến ở core có lợi cho mọi lĩnh vực.
- **Domain pack** là đơn vị để mở rộng. Lĩnh vực mới chỉ cần một `domain.toml` và một vài file trong overlay, không phải viết agent mới.
- **Project** ghi lại phiên bản archwright và domain pack đã dùng trong `project.toml`. Nhờ đó biết bài học nào có thể đưa lên, và dự án nào cần nâng cấp khi domain pack có bản mới.
- Mỗi domain pack là một thư mục `domains/<tên-domain-pack>/` (ví dụ [domains/embedded-mcu/](../domains/embedded-mcu/README.md)), chứa mọi thứ của domain: `domain.toml` và `overlay/` (tham gia sinh dự án), cùng gói sơ đồ `src/`, `dist/` và ghi chép nghiên cứu (chỉ mô tả, không tham gia sinh dự án). Hiện các domain mới có phần sơ đồ và nghiên cứu. Công cụ build sơ đồ nằm trong [.archify/](../.archify/README.md).

## 3. Tri thức: hai đường xử lý

| | Đường **grep** | Đường **distill** |
| --- | --- | --- |
| Dùng cho | Thứ cần CHÍNH XÁC: số liệu, bảng, thanh ghi, điều khoản | Thứ cần PHÁN ĐOÁN: quy tắc, framework, anti-pattern |
| Công cụ | `kit/ingest.py` (dùng lại extractor của book-to-skill) | book-to-skill với `BOOK_TO_SKILL_SCOPE=project` |
| Đầu ra | `refs/<slug>.txt` | `.claude/skills/<slug>/` (tối đa 5) |
| Rủi ro nếu dùng sai | Ít: đây là văn bản gốc | Tóm tắt làm mất hoặc làm lệch con số, nên **không** dùng làm nguồn số liệu |

Tri thức nội bộ (`docs/`) lúc đầu được tra bằng `rg`; chỉ khi có khoảng 50 issue trở lên mới gộp thành một skill dự án.

## 4. Agent: 4 vai trò chung, chuyên môn hoá bằng checklist

| Agent | Quyền | Đầu vào chuyên ngành |
| --- | --- | --- |
| `builder` | sửa | `CLAUDE.md`, `decisions.md`, `checklists/review.md` |
| `reviewer` | chỉ đọc | `checklists/review.md`, `decisions.md`, `refs/` |
| `verifier` | chỉ đọc + chạy lệnh | `tools/verify.toml` |
| `curator` | sửa tài liệu, không sửa sản phẩm | mẫu ghi chép, `SOURCES.md`, evals |

Lý do không tạo agent riêng cho từng lĩnh vực: số agent tăng thì mô tả của chúng chồng lấn nhau và agent dễ bị gọi nhầm. Chuyên môn nằm ở **checklist, verify.toml và skill**, những thứ domain pack thay được.

Luồng một thay đổi: `builder → reviewer → verifier → curator`. Chỉ `verifier` được nói PASS. Đây là luồng gợi ý, không bắt buộc: domain pack và dự án mô tả vòng lặp của mình bằng các *bước* ([core-model.md §3](core-model.md#3-bước-một-khái-niệm-thay-cho-mọi-slot)), thêm, bớt hay đổi vai trò tuỳ nhu cầu. Ví dụ [domain nhúng](../domains/embedded-mcu/README.md) thêm bước `design` do `planner` làm và bước kiểm chứng chậm HIL.

## 5. Vòng đời tri thức

```text
làm việc → ghi (decision / issue, 2 phút) → curator dọn hằng tuần
   ↑                                              │
   │                                              ▼
agent dùng ← skill/refs/docs cập nhật ← eval chấm lại (điểm giảm = tri thức cũ)
                                              │
                                              ▼
                          bài học đúng cho cả lĩnh vực → đề xuất diff lên domain pack
```

## 6. Chuyển sang lĩnh vực mới

1. `cp -r domains/_template domains/<linh-vuc>`.
2. Mô tả domain bằng các khái niệm của [mô hình core](core-model.md#5-mô-tả-bằng-file) (mọi mục đều tuỳ chọn), bắt đầu từ **4 trục chẩn đoán** (khác với 4 khối ở §1): kiểm chứng nhanh hay chậm, cần chính xác hay phán đoán, tri thức riêng nhiều hay ít, hậu quả khi sai lớn hay nhỏ.
3. Viết checklist rà soát (lỗi hay gặp nhất của lĩnh vực) và `verify.toml` (cái gì xác nhận "đúng"). Nếu chưa có cách kiểm chứng tự động, bước đầu tiên có thể là một script chấm theo rubric.
4. `python kit/new_project.py <ten> --domain <linh-vuc>`.

Ví dụ ánh xạ vòng kiểm chứng: nhúng → build/test/HIL; nội dung giáo dục → chạy thử với trẻ và đo tỉ lệ hoàn thành bài; marketing → A/B test; pháp lý → luật sư rà soát theo checklist điều khoản.

## 7. Brainstorm: ý tưởng mở rộng (chưa hiện thực)

Xếp theo mức độ nên làm. Mỗi ý tưởng chỉ đưa vào archwright khi đã đo được lợi ích (nguyên tắc "đo, đừng khẳng định" của book-to-skill).

### Nên làm sớm

- **Kickoff interview**: agent phỏng vấn product owner khoảng 15 câu rồi điền mục tiêu, non-goals và D-001 trong `CLAUDE.md`. Dự án có hướng ngay từ giờ đầu.
- **Kiểm ngân sách tự động** (`kit/lint.py`): đếm dòng `CLAUDE.md`, đếm skill, tìm thông tin bị lặp, tìm con số không kèm nguồn trong `decisions.md`. Có thể chạy trong CI.
- **Hook nhắc ghi chép**: khi commit có chữ "fix" mà không có issue tương ứng thì hook nhắc ghi issue. Chỉ nhắc, không chặn.
- **Phase gate**: mỗi domain pack định nghĩa các giai đoạn (ví dụ nhúng: kiến trúc → schematic → bring-up → kiểm định) cùng điều kiện qua cổng, đặt trong `docs/gates.md`.

### Làm khi có 2–3 dự án

- **Promotion có bằng chứng**: script gom các dòng "Bài học" đã kiểm chứng từ nhiều dự án, chỉ đề xuất đưa lên domain pack những bài học xuất hiện từ 2 dự án trở lên.
- **Nâng cấp dự án**: dựa vào `project.toml`, so sánh với domain pack mới và đề xuất diff (giống cách cập nhật template).
- **Eval chung của lĩnh vực**: câu hỏi seed của domain pack được chấm trên mọi dự án để phát hiện domain pack nào đang yếu.
- **Kho domain pack dạng git**: mỗi pack có phiên bản; dự án ghim phiên bản.

### Thử nghiệm (giả thuyết, cần đo)

- **Red-team agent**: đóng vai phản biện trước các quyết định lớn.
- **Kiểm độ tươi**: đánh dấu tri thức cũ khi nguồn trong `refs/` có bản mới hơn (dùng fingerprint sha256 mà book-to-skill đã ghi).
- **Sổ chi phí**: ghi token và thời gian cho mỗi lần chưng cất hay chạy agent để biết đâu đáng đầu tư.
- **Onboarding bằng hỏi đáp**: người mới hỏi dự án thay vì đọc tài liệu; câu hỏi trả lời sai sẽ thành eval mới.

### Không làm

- Một agent cho mỗi chuyên môn nhỏ.
- Chưng cất datasheet (dùng đường grep, §3).
- Tự động đưa bài học lên domain pack mà không có người duyệt.
- Một kho skill khổng lồ dùng chung cho mọi dự án.

## 8. Demo: dự án nhúng `examples/soil-node`

Dự án minh hoạ là nút cảm biến độ ẩm đất chạy pin. Toàn bộ khung được sinh bằng một lệnh:

```bash
python kit/new_project.py soil-node --domain embedded-mcu --out examples/soil-node
```

Sau đó điền phần minh hoạ (có đánh dấu `DEMO`):

- `CLAUDE.md`: mục tiêu, non-goals, giai đoạn hiện tại.
- `docs/decisions.md`: D-001 chọn SoC, D-002 chọn cảm biến, D-003 ngân sách pin là ràng buộc gốc. Con số để dạng `<?>` cho tới khi nạp datasheet, đúng với quy tắc "không có nguồn thì không ghi số".
- `docs/issues/001-*.md`: một lỗi đang mở, nguyên nhân mới là giả thuyết, cùng một bài học ứng viên để đưa lên domain pack sau khi kiểm chứng.

Kịch bản ngày đầu:

| Bước | Ai | Lệnh / việc | Kết quả |
| --- | --- | --- | --- |
| 1 | Người | Tạo dự án bằng lệnh trên | Khung đủ 5 chức năng |
| 2 | `curator` | Đặt datasheet, errata của SoC và cảm biến vào `refs/sources/`, chạy `python ../../kit/ingest.py refs/sources/*.pdf --mode technical --out refs/` | `refs/<part>-datasheet.txt`, thêm dòng vào `SOURCES.md` |
| 3 | `curator` | Điền đáp án cho câu S1–S5 trong `docs/evals.md` từ refs; thay `<?>` trong D-001…D-003 | Quyết định có nguồn |
| 4 | `curator` | (Tuỳ chọn) chưng cất 1–2 sách nền tảng thành skill | `.claude/skills/` |
| 5 | Người | Bật các bước `build` / `host-tests` trong `tools/verify.toml` khi đã có mã nguồn | `verify.py` chuyển từ BLOCKED sang PASS/FAIL thật |
| 6 | `builder → reviewer → verifier` | Thực hiện tính năng đầu tiên (đọc ADC rồi ngủ sâu) | Thay đổi có bằng chứng PASS |

Ngay sau bước 1, `python tools/verify.py` phải trả `VERDICT: BLOCKED` (exit 2) vì chưa bật bước nào: hệ thống không được báo PASS khi chưa kiểm chứng gì.
