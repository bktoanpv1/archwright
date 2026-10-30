---
id: PT-LLM-AGENT
type: report
form: paper-test
status: superseded
origin: authored
---

# Thử giấy: domain `llm-agent`

Mục đích: điền hợp đồng core v0.1 cho một domain khác xa domain nhúng, **không được sửa core**. Chỗ nào không điền được là lỗ hổng của core.

> **Ghi chú:** hợp đồng v0.1 đã được thay bằng [mô hình khái quát v0.2](../core-model.md), không còn phần bắt buộc. 7 lỗ hổng dưới đây được diễn đạt bằng khái niệm sẵn có của v0.2 ([core-model.md §7](../core-model.md#7-liên-hệ-với-các-vấn-đề-đã-gặp)). Tài liệu này giữ lại làm bằng chứng cho lý do đổi hướng.

Domain: ứng dụng agent LLM hội thoại theo thời gian thực (giọng nói, có công cụ, có kịch bản bài học), người dùng là trẻ em. Đặc điểm domain được lấy từ `robot-lesson-agent` **chỉ để biết domain này trông thế nào**; dự án đó không phải chuẩn để archwright làm theo.

## 1. Chẩn đoán theo 4 trục

| Trục | Giá trị | Lý do |
| --- | --- | --- |
| `verification_speed` | `low` | Unit test thì nhanh, nhưng hành vi chỉ đo được bằng eval hội thoại: chậm, tốn token, kết quả dao động giữa các lần chạy |
| `precision_need` | `high` / `low` | Hai nửa khác nhau: giao thức, schema, giá và giới hạn của model cần chính xác; chất lượng hội thoại cần phán đoán |
| `private_knowledge` | `high` | Kịch bản bài học, đồ thị bot, checkpoint, prompt đều là tri thức riêng |
| `failure_cost` | `high` | Người dùng là trẻ em: an toàn nội dung, quyền riêng tư; ngoài ra còn chi phí token |

`precision_need` không gói được vào một giá trị → **trục cần cho phép giá trị theo từng phần**, hoặc pack phải chọn bên nặng hơn. Đây là lỗ hổng nhỏ, ghi nhận ở §5 (A1).

## 2. Điền 5 chức năng

| Chức năng | Điền cho `llm-agent` | Vừa với v0.1? |
| --- | --- | --- |
| **Nguồn gốc** | Grep: tài liệu API và SDK của nhà cung cấp model, giao thức WebSocket/gRPC, bảng giá và giới hạn model. Distill: kỹ thuật prompt, thiết kế agent, an toàn trẻ em. | **Một phần.** Nguồn thật của lỗi là **trace và hội thoại thật** (Datadog LLM Obs, Langfuse, khiếu nại phụ huynh). v0.1 chỉ có tài liệu tĩnh → C5 |
| **Nhật ký tri thức** | `decisions`, `issues`, cộng thêm `prompt-changelog` (lý do đổi prompt) và `known-failures` (mẫu hội thoại hỏng → nguyên nhân) | Vừa, nhờ `extra_records` |
| **Bản đồ** | `CLAUDE.md` trỏ tới cách chạy local, quy tắc config, nơi ở của prompt và cấu hình bot | **Một phần.** Prompt và đồ thị bot nằm ở Langfuse và DB, không nằm trong repo; bản đồ phải trỏ ra ngoài và ghi được phiên bản → C1 |
| **Kiểm chứng** | Nhanh: lint, type check, unit test, test giao thức. Chậm: bộ eval theo tính năng (routing: recall, precision, p95 latency; chất lượng: pass rate do LLM judge chấm), replay hội thoại thật, eval an toàn, đo TTFT, test tải | **Không vừa.** PASS/FAIL theo exit code không biểu diễn được "recall ≥ 0.9 so với baseline, chạy 3 lần" → C2. Mỗi tính năng chỉ cần chạy lại vùng bị ảnh hưởng → C3 |
| **Chưng cất** | Skill: thiết kế prompt, thiết kế tool, an toàn trẻ em. Kiểm tra tri thức của agent về dự án | **Va chạm tên.** `docs/evals.md` của core (kiểm tra agent hiểu dự án) trùng tên với eval sản phẩm → C7 |

## 3. Điền slot workflow

| Slot | Điền | Vừa với v0.1? |
| --- | --- | --- |
| `design` | Agent thiết kế viết spec thay đổi: thay đổi nằm ở code, prompt hay đồ thị bot; tiêu chí eval nào phải đạt | Vừa (`inherits = "builder"`) |
| ◆ duyệt thiết kế | Bắt buộc khi đổi hành vi với trẻ (an toàn, nội dung) | Vừa |
| `fast_gates` | lint, type, unit, test giao thức, kiểm schema đồ thị bot | Vừa |
| `slow_verification` | Eval theo tính năng và replay; chính sách: chạy theo `impact_zones`, ngân sách token mỗi lần, chạy N lần để trừ dao động | **Một phần.** Chính sách 3 câu viết được, nhưng bước không diễn đạt được ngưỡng và baseline → C2, C3 |
| ◆ duyệt merge | Người duyệt đọc báo cáo eval, kèm mẫu hội thoại hỏng | Vừa |
| *(thiếu)* | Canary trên một nhóm robot, theo dõi trace và chỉ số an toàn, rollback prompt nếu xấu đi | **Không có slot.** Vòng lặp của core dừng ở merge, trong khi với domain này kiểm chứng thật chỉ có sau triển khai → C4 |

**Thay đổi không đi qua git.** Sửa prompt trên Langfuse hay sửa đồ thị bot qua API backend có hiệu lực ngay, không qua `builder → reviewer → verifier`. Nếu vòng lặp chỉ áp cho git, phần lớn thay đổi hành vi nằm ngoài kiểm soát → C1. Agent ghi vào hệ thống ngoài cũng cần một loại quyền riêng (có phiên bản, hoàn tác được) → C6.

## 4. Phác thảo `verify.toml` và chỗ vỡ

```toml
[steps.unit]
tier = "fast"
run = "uv run pytest tests/module -q"          # vừa: exit code → PASS/FAIL

[steps.routing-eval]
tier = "slow"
run = "uv run python tests/eval/run.py --line pivot_talk --json"
# v0.1 KHÔNG diễn đạt được ba điều dưới đây:
metric = { recall = ">= 0.90", precision = ">= 0.85", latency_p95_ms = "<= 1800" }   # C2
baseline = "main@last-pass"; repeat = 3; aggregate = "median"                          # C2
when = { impact_zones = ["pivot", "continue"] }                                        # C3
```

## 5. Kết quả

| Kết quả | Số chỗ | Chi tiết |
| --- | --- | --- |
| Vừa, không cần sửa | 9 | 4 vai trò, BLOCKED ≠ PASS, hai đường tri thức, `extra_records`, slot `design` và `fast_gates`, hai cổng người, luật tối đa 3 vòng, `inherits` |
| Lỗ hổng của core | 7 | C1–C7 (v0.1); cách v0.2 diễn đạt: [core-model.md §7](../core-model.md#7-liên-hệ-với-các-vấn-đề-đã-gặp) |
| Lỗ hổng nhỏ | 1 | A1: trục chẩn đoán cần cho phép giá trị theo từng phần (`precision_need = { protocol = "high", quality = "low" }`) |

**Kết luận.** Khung 3 tầng, 4 vai trò và luật kiểm chứng đứng vững khi gặp domain thứ hai. Phần vỡ tập trung ở một chỗ: core v0.1 ngầm giả định rằng **mọi thay đổi nằm trong git và mọi kiểm chứng là PASS/FAIL tất định trước khi merge**. Domain LLM agent phá cả hai giả định. 5 trong 7 lỗ hổng (C1–C5) cũng giải quyết được những điểm domain nhúng đang tự xử lý riêng, như ngân sách bộ nhớ, chính sách HIL và OTA. Vì vậy đây là thiếu sót của core, không phải đặc thù của AI.

## 6. Bước tiếp theo đề xuất

1. Người duyệt chọn C1–C7 nào đưa vào core v0.2.
2. Viết lại mô tả của `embedded-mcu` theo v0.2 và kiểm tra lại không vỡ.
3. ~~Tạo gói sơ đồ `llm-agent`~~ Đã làm: [llm-agent/](../../domains/llm-agent/README.md).
