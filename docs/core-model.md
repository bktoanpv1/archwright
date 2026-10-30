---
id: CORE-MODEL
type: description
form: design-note
status: draft
origin: authored
---

# Mô hình khái quát của core (v0.2, đề xuất)

Core của archwright không quy định một dự án *phải có* gì. Core cung cấp một **bộ khái niệm chung** đủ để mô tả bất kỳ dự án nào: firmware, agent LLM, nội dung giáo dục, pháp lý. Mô tả bằng cùng bộ khái niệm thì mọi dự án có cùng một cách nhìn tổng quan và so sánh được với nhau, dù bên trong khác hẳn nhau.

Bối cảnh: [architecture.md](architecture.md). Bản v0.1 theo hướng hợp đồng bắt buộc (trường bắt buộc, slot cố định) đã được thay bằng bản này. Ví dụ mô tả domain LLM agent: [paper-tests/llm-agent.md](paper-tests/llm-agent.md).

## 1. Nguyên tắc thiết kế

- **Mô tả, không quy định.** Mọi phần của mô hình đều tuỳ chọn. Một dự án có thể không có bước thiết kế, không có người duyệt, không có tri thức chưng cất. Mô hình chỉ cần diễn đạt được điều đó, và diễn đạt trung thực.
- **Khái quát, không liệt kê.** Thay vì thêm một slot cho mỗi trường hợp (HIL, eval, canary…), core có một khái niệm đủ rộng để chứa tất cả (ở đây là *bước kiểm chứng* với tốc độ, chi phí, điều kiện kích hoạt và loại bằng chứng).
- **Mặc định, không bắt buộc.** Domain pack là một bộ giá trị mặc định viết bằng cùng bộ khái niệm. Dự án nhận mặc định rồi thêm, bớt, đổi tuỳ ý.
- **Tổng quan sinh từ mô tả.** Sơ đồ tổng quan và sơ đồ vòng lặp của mọi dự án được dựng từ cùng một mô tả, nên luôn có cùng các góc nhìn.

## 2. Bảy khái niệm

| Khái niệm | Trả lời câu hỏi | Thuộc tính chính |
| --- | --- | --- |
| **Artefact** | Dự án thay đổi *cái gì*? | nơi lưu (git, hệ thống ngoài, thiết bị), cách ghi phiên bản, cách hoàn tác |
| **Nguồn tri thức** | Thông tin đúng *ở đâu*? | độ chính xác cần (tra nguyên văn hay phán đoán), cách truy cập (grep, chưng cất, truy vấn), độ tươi; gồm cả bằng chứng runtime (log, trace, phản hồi người dùng) |
| **Vai trò** | *Ai* làm, được phép làm gì? | người, agent hoặc công cụ; quyền đọc/ghi trên từng artefact |
| **Bước** | Một thay đổi đi qua *những gì*? | loại (§3), vai trò thực hiện, tốc độ, chi phí, điều kiện kích hoạt |
| **Bằng chứng** | Làm sao biết *đúng*? | dạng: nhị phân (exit code), chỉ số (ngưỡng, baseline, số lần lặp), phán đoán (người hoặc rubric) |
| **Phán quyết** | Kết luận *là gì*? | PASS / FAIL / BLOCKED, tính từ bằng chứng; ai được kết luận |
| **Vòng phản hồi** | Học được gì, *quay về đâu*? | từ bằng chứng hoặc sự cố về nguồn tri thức, về domain pack |

5 chức năng ở [architecture.md §1](architecture.md#1-ý-tưởng-cốt-lõi) là 5 câu hỏi nhìn vào các khái niệm này: *nguồn gốc* nhìn vào nguồn tri thức, *nhật ký tri thức* và *chưng cất* nhìn vào vòng phản hồi, *bản đồ* nhìn vào vai trò, *kiểm chứng* nhìn vào bước, bằng chứng và phán quyết. Câu trả lời "dự án này không có" là hợp lệ.

## 3. Bước: một khái niệm thay cho mọi slot

Mỗi bước có một **loại**. Loại chỉ dùng để vẽ và so sánh, không quy định thứ tự hay số lượng:

| Loại | Ví dụ ở domain nhúng | Ví dụ ở domain LLM agent |
| --- | --- | --- |
| `design` | planner viết spec module | viết spec thay đổi prompt và đồ thị bot |
| `make` | builder sửa firmware | sửa code, prompt, cấu hình bot |
| `check` | build, test, ngân sách bộ nhớ, HIL | unit test, eval theo tính năng, replay |
| `decide` | duyệt thiết kế, duyệt merge | duyệt merge kèm báo cáo eval |
| `release` | OTA theo đợt | đổi phiên bản prompt, canary |
| `observe` | telemetry thiết bị | trace hội thoại, chỉ số an toàn |
| `learn` | ghi lỗi đã biết, bài học | biến hội thoại hỏng thành ca test mới |

Thuộc tính của một bước đủ để diễn đạt các trường hợp khác nhau mà không cần khái niệm riêng:

- `speed` và `cost`: phân biệt kiểm chứng nhanh, rẻ với kiểm chứng chậm, khan hiếm (HIL, eval tốn token).
- `when`: điều kiện kích hoạt theo artefact hoặc vùng ảnh hưởng ("chỉ chạy HIL khi đổi driver", "chỉ chạy eval routing khi đổi pivot").
- `evidence`: nhị phân, chỉ số hoặc phán đoán.
- `on_unavailable`: điều xảy ra khi bước không chạy được (thường là BLOCKED và một người quyết).

Vòng lặp của một dự án là một đồ thị các bước. archwright gợi ý một hình mẫu (`design → make → check → decide → release → observe → learn`), nhưng dự án có thể bỏ, lặp hoặc đảo bước.

## 4. Thứ bất biến duy nhất: nguyên lý, không phải cấu trúc

Core không bắt dự án có phần nào. Core chỉ giữ ba nguyên lý về **tính trung thực** của mô tả, vì thiếu chúng thì cái nhìn tổng quan không còn đáng tin:

1. **Phán quyết theo bằng chứng.** Không có bằng chứng thì là BLOCKED, không phải PASS.
2. **Con số có nguồn.** Một con số trong quyết định hay tài liệu phải trỏ được tới nguồn tri thức, hoặc ghi rõ là giả định.
3. **Người giữ quyền quyết.** Mô hình ghi rõ quyết định nào do người đưa ra. Bao nhiêu quyết định giao cho AI là lựa chọn của từng dự án.

## 5. Mô tả bằng file

Một dự án hay domain pack mô tả mình trong một file TOML. Mọi mục đều tuỳ chọn; file nhỏ nhất hợp lệ chỉ có `name`.

```toml
name = "soil-node"
extends = "embedded-mcu@0.2"                 # tuỳ chọn: nhận mặc định của domain pack

[[artefact]]
id = "firmware";  store = "git"
[[artefact]]
id = "device-config";  store = "external";  versioned = true;  revert = "push bản cũ"

[[source]]
id = "soc-datasheet";  access = "grep";  precision = "exact"
[[source]]
id = "field-telemetry";  access = "query";  kind = "runtime"

[[step]]
id = "hil";  kind = "check";  speed = "slow";  cost = "bench"
when = { artefact = "firmware", paths = ["drivers/**", "power/**"] }
evidence = { type = "metric", metric = "sleep_current_uA", threshold = "<= 20", repeat = 3 }
on_unavailable = "blocked"

[[step]]
id = "ota-canary";  kind = "release"        # dự án khác có thể không có bước này

[[loop]]
from = "field-telemetry";  to = "known-failures";  via = "curator"
```

Quy tắc kế thừa đơn giản: mục cùng `id` thì dự án đè pack; mục mới thì thêm; ghi `remove = true` để bỏ một mục của pack.

## 6. Tổng quan sinh từ mô tả

Vì mọi dự án dùng cùng 7 khái niệm, cùng một bộ góc nhìn áp được cho tất cả:

| Góc nhìn | Dựng từ | Loại sơ đồ archify |
| --- | --- | --- |
| Tổng quan | artefact, nguồn tri thức, vai trò | `architecture` |
| Vòng lặp thay đổi | bước, phán quyết | `workflow` |
| Vòng phản hồi tri thức | nguồn tri thức, vòng phản hồi | `dataflow` |

4 khối trong các gói sơ đồ hiện tại (tri thức, agent & công cụ, workflow, mô hình hoá domain) là một cách nhóm các góc nhìn này cho người đọc, không phải một phần của mô hình.

## 7. Liên hệ với các vấn đề đã gặp

Thử mô tả domain LLM agent ([paper-tests/llm-agent.md](paper-tests/llm-agent.md)) từng làm lộ 7 lỗ hổng của bản hợp đồng v0.1. Ở bản khái quát, cả 7 đều được diễn đạt bằng khái niệm sẵn có, không cần thêm quy định:

| Lỗ hổng | Diễn đạt trong mô hình |
| --- | --- |
| C1 thay đổi nằm ngoài git (prompt, cấu hình) | artefact có `store = "external"` |
| C2 kiểm chứng cho ra chỉ số dao động | bằng chứng dạng `metric` với ngưỡng, baseline, `repeat` |
| C3 chỉ chạy lại vùng bị ảnh hưởng | `when` của bước |
| C4 kiểm chứng thật chỉ có sau triển khai | bước loại `release` và `observe` |
| C5 nguồn lỗi là trace và khiếu nại | nguồn tri thức `kind = "runtime"` và một vòng phản hồi |
| C6 agent ghi ra hệ thống ngoài | quyền của vai trò trên artefact `external` |
| C7 trùng tên "eval" | không còn tên file cố định; mỗi dự án tự đặt |
| A1 một trục có hai giá trị | trục chẩn đoán gắn với từng artefact hoặc nguồn, không gắn với cả domain |
