# Domain: LLM Agent System

Gói sơ đồ của domain pack `llm-agent`: sản phẩm xây trên LLM có công cụ và hội thoại (chatbot, voice agent, agent theo kịch bản). Quy ước và cách build: [.archify/README.md](../../.archify/README.md). Mô hình khái quát dùng chung: [docs/core-model.md](../../docs/core-model.md); thử giấy đã dẫn tới mô hình đó: [docs/paper-tests/llm-agent.md](../../docs/paper-tests/llm-agent.md). Căn cứ và nguồn của mọi khẳng định dưới đây: [research.md](research.md).

## Sơ đồ

| # | Sơ đồ | Loại | Nguồn | Xem |
| --- | --- | --- | --- | --- |
| 01 | Tổng quan 4 khối, thêm phần vận hành (production qua gateway, trace đã lọc PII) | architecture | [src](src/01-overview.architecture.json) | [dist](dist/01-overview.html) |
| 02 | Vòng lặp một thay đổi: spec → duyệt → sửa code/prompt/cấu hình → kiểm nhanh + eval dev → review → eval held-out + red team → duyệt phát hành → shadow, canary → giữ hay chuyển nhãn về → chuyên gia gán nhãn → học lại | workflow | [src](src/02-feature-loop.workflow.json) | [dist](dist/02-feature-loop.html) |
| 03 | Vòng đời một phiên bản prompt, cấu hình hoặc model: nháp → qua eval dev → duyệt → canary → production; BLOCKED, rollback, chờ đổi model, bị thay thế | lifecycle | [src](src/03-version.lifecycle.json) | [dist](dist/03-version.html) |
| 04 | Vòng dữ liệu: hội thoại thật → lọc PII, eval online → chuyên gia gán nhãn → lỗi đã biết, eval dev, held-out, judge → builder và verifier | dataflow | [src](src/04-eval-flywheel.dataflow.json) | [dist](dist/04-eval-flywheel.html) |

## 4 khối của domain

| Khối | Nội dung trong domain này |
| --- | --- |
| **1 · Tri thức** | Tài liệu nhà cung cấp model, SDK, giao thức (chỉ trích xuất, ghi ngày tra; tên model, giá, tham số, lịch ngừng hỗ trợ cũ rất nhanh) · Hướng dẫn của Anthropic, OpenAI và người làm nghề về agent, công cụ, context, eval (chưng cất) · An toàn: OWASP LLM 2025, OWASP Agentic 2026, NIST AI 600-1; luật về trẻ em và dữ liệu cá nhân (chỉ mã điều khoản) · Tri thức nội bộ: decisions, lỗi đã biết (mẫu hội thoại → nguyên nhân → trạng thái), bộ eval dev, held-out, judge · Bằng chứng runtime: trace đã lọc PII, phản hồi, khiếu nại |
| **2 · Agent & công cụ** | Eval harness (bộ dev, bộ held-out, judge nhị phân đã hiệu chỉnh, chạy N lần, pass^k, so cặp) · red team (promptfoo trong CI, garak, PyRIT nhiều lượt) · quan sát theo OTel GenAI (Langfuse, Datadog LLM Obs hoặc tương đương): trace, eval online, hàng đợi gán nhãn · prompt registry có nhãn · gateway model (retry, dự phòng, circuit breaker) · gitnexus (impact analysis) |
| **3 · Workflow** | planner → duyệt thiết kế → builder (code, prompt, cấu hình) → kiểm nhanh + eval dev → reviewer → eval held-out + red team (vùng ảnh hưởng) → verifier → duyệt phát hành → shadow, canary + quan sát → verifier (giữ hay chuyển nhãn về) → chuyên gia gán nhãn → curator (ca eval, judge, lỗi đã biết) |
| **4 · Mô hình hoá domain** | Artefact gồm cả prompt, cấu hình và snapshot model ngoài git; trạng thái nằm ở nhãn, chuyển nhãn là phát hành · Bằng chứng dạng chỉ số dao động: N lần, pass^k, so cặp, gom theo hội thoại · Builder không được ghi bộ eval, judge, held-out · Có phán quyết sau phát hành · Sự kiện từ bên ngoài (model ngừng hỗ trợ) kích hoạt vòng lặp · Hội thoại thật là dữ liệu cá nhân: cổng PII và đồng ý trước khi thành ca eval |

## Các bước

Mô tả bằng thuộc tính bước của [core-model §3](../../docs/core-model.md#3-bước-một-khái-niệm-thay-cho-mọi-slot). Tốc độ và chi phí là ước lượng định tính.

| Bước | Loại | Vai trò | Tốc độ · chi phí | Bằng chứng | Khi không chạy được |
| --- | --- | --- | --- | --- | --- |
| Spec thay đổi và tiêu chí eval | `design` | planner | giờ | phán đoán | |
| Duyệt thiết kế | `decide` | người | | phán đoán; bắt buộc khi đổi hành vi với người dùng hoặc an toàn | |
| Sửa code, prompt, cấu hình, công cụ | `make` | builder | phút–giờ | | |
| Kiểm nhanh: lint, type, unit, schema đồ thị bot, eval dev | `check` | công cụ | phút | nhị phân + chỉ số trên bộ dev | BLOCKED |
| Review | `check` | reviewer (subagent mới, chỉ đọc diff) | | phán đoán theo checklist | |
| Eval held-out theo vùng ảnh hưởng | `check` | verifier | chậm, tốn token | chỉ số: pass^k qua N lần, so cặp với baseline, ngưỡng theo tính năng | BLOCKED, người quyết |
| Red team | `check` | verifier + công cụ | chậm | chỉ số: tỉ lệ tấn công thành công theo nhóm OWASP | BLOCKED |
| Duyệt phát hành | `decide` | người | | báo cáo eval, diff prompt, mẫu hỏng, tác động chi phí | |
| Shadow, canary | `release` | công cụ | giờ–ngày | | |
| Quan sát | `observe` | công cụ | liên tục | chỉ số online: điểm judge trên mẫu, p95, chi phí mỗi phiên, lỗi công cụ, tỉ lệ dự phòng | |
| Giữ hay chuyển nhãn về | `decide` | verifier đề xuất, người quyết khi mơ hồ | phút | ngưỡng trên khoảng tin cậy | |
| Gán nhãn lỗi | `learn` | chuyên gia sản phẩm; agent gom cụm | giờ mỗi tuần | phán đoán | |
| Ca eval, judge, lỗi đã biết | `learn` | curator | | | |

Điều kiện kích hoạt (`when`) đáng ghi: chỉ chạy eval của tính năng trong vùng ảnh hưởng; sửa định nghĩa công cụ thì đo lại chi phí vì mất prompt cache; đổi model thì chạy đủ bộ eval ở vài mức effort; đổi hành vi với trẻ em thì thêm eval an toàn và duyệt thiết kế.

## Quy tắc cho agent

Rút từ bằng chứng ở [research.md](research.md). Đây là nội dung đề xuất cho `checklists/review.md` và cấu hình quyền của pack.

1. Không đọc, không sửa bộ held-out, judge prompt và bộ chấm khi đang làm builder. Chặn bằng deny rule hoặc hook; dặn "đừng gian lận" không đủ ([research.md §1.5](research.md#15-agent-lập-trình-tự-lách-eval)).
2. Tối ưu prompt và công cụ trên bộ dev; kết quả báo cáo là kết quả trên held-out.
3. Mọi thay đổi prompt, schema công cụ, tham số model đi thành diff cho người duyệt, kèm điểm eval trước/sau, mẫu hội thoại và tác động chi phí.
4. Tên model, giá, giới hạn, tham số được hỗ trợ, API SDK: không trả lời từ trí nhớ; tra tài liệu (llms.txt, MCP tài liệu), ghi ngày tra.
5. Ghim snapshot model có ngày và phiên bản SDK; đổi model là một thay đổi đầy đủ, không phải sửa cấu hình.
6. Mọi trace ghi phiên bản prompt, snapshot model, hash cấu hình, commit; dùng prompt dự phòng thì báo lỗi rõ.
7. Phân tích lỗi: agent lấy mẫu trace và gom cụm làm nháp; chuyên gia sản phẩm gán nhãn; judge được kiểm bằng TPR/TNR trên nhãn người.
8. Chấm kết quả và trạng thái, không chấm đường đi; mỗi lần chạy từ môi trường sạch; đọc transcript trước khi tin điểm số.
9. Bắt đầu bằng workflow đơn giản nhất; chỉ thêm nút, công cụ hay quyền tự chủ khi eval cho thấy lợi ích.
10. Văn bản từ công cụ, tài liệu truy xuất, người dùng là không tin cậy; không được kích hoạt hành động có hậu quả. Công cụ có hậu quả không hoàn tác được cần người xác nhận.
11. Không đưa hội thoại thật vào bộ eval khi chưa qua lọc PII và chưa có cơ sở đồng ý.

## Mô tả theo mô hình core (phác thảo)

Phác thảo `domain.toml` theo [core-model §5](../../docs/core-model.md#5-mô-tả-bằng-file); chỉ một phần.

```toml
name = "llm-agent"

[[artefact]]
id = "code";    store = "git"
[[artefact]]
id = "prompts"; store = "external";  versioned = true;  revert = "chuyển nhãn production về bản trước"
[[artefact]]
id = "bot-config"; store = "external";  versioned = true
[[artefact]]
id = "model-choice"; store = "git";  revert = "chỉ khi snapshot cũ chưa retire"
[[artefact]]
id = "eval-heldout"; store = "git";  writers = ["curator", "human"]   # builder không có quyền ghi

[[source]]
id = "provider-docs";  access = "grep";  precision = "exact";  freshness = "ghi ngày tra"
[[source]]
id = "traces";  access = "query";  kind = "runtime";  pii = "redacted"

[[step]]
id = "heldout-eval";  kind = "check";  speed = "slow";  cost = "tokens"
when = { impact_zones = ["routing", "lesson-flow"] }
evidence = { type = "metric", metric = "pass_hat_k", k = 3, threshold = ">= baseline", compare = "paired" }
on_unavailable = "blocked"

[[step]]
id = "canary";  kind = "release"
[[step]]
id = "model-deprecation";  kind = "design";  trigger = "provider notice"

[[loop]]
from = "traces";  to = "eval-dev";  via = "human-annotation"
```

Các trường `writers`, `freshness`, `pii`, `trigger`, `compare` chưa có trong core-model v0.2; chúng là đề xuất từ lần hoàn thiện gói này và cần chốt ở core trước khi dùng. `writers` cùng nhu cầu với `shared_with` của [pcb-design](../pcb-design/README.md#mô-tả-theo-mô-hình-core-phác-thảo): quyền ghi theo vai trò trên từng artefact.

## So với `embedded-mcu`

| | `embedded-mcu` | `llm-agent` |
| --- | --- | --- |
| Artefact | firmware trong git | code trong git, prompt và cấu hình ngoài git, snapshot model |
| Kiểm chứng chậm | HIL bench (tài nguyên vật lý) | eval held-out (token, thời gian, kết quả dao động) |
| Dạng bằng chứng | chủ yếu nhị phân, thêm ngân sách bộ nhớ và dòng ngủ | chủ yếu chỉ số: pass^k, so cặp với baseline |
| Rủi ro riêng của agent lập trình | sửa test cho qua | lách bộ chấm eval, overfit prompt vào ca eval |
| Sau merge | OTA theo đợt, telemetry, giữ hay rollback | shadow, canary, quan sát, chuyển nhãn về |
| Thay đổi từ bên ngoài | errata chip | model ngừng hỗ trợ, API SDK đổi |
| Nguồn lỗi thật | log serial, telemetry | trace hội thoại, khiếu nại (dữ liệu cá nhân) |

Hai gói dùng cùng các khái niệm của [mô hình khái quát](../../docs/core-model.md); khác nhau ở giá trị, không ở cấu trúc.

## Ghi chú

- Đặc điểm domain lấy từ một dự án voice agent cho trẻ em chỉ để biết domain trông thế nào; gói này không lấy dự án đó làm chuẩn.
- Luật trẻ em và dữ liệu cá nhân ở [research.md §4.1](research.md#41-trẻ-em-và-dữ-liệu-cá-nhân) là tóm tắt từ nguồn thứ cấp, không phải tư vấn pháp lý; dự án có người dùng là trẻ em cần người có chuyên môn pháp lý duyệt.
- Voice agent thêm các chỉ số riêng (thời gian tới âm thanh đầu tiên, ngắt lời, WER) và cần eval ở chế độ âm thanh; gói chưa vẽ riêng phần này.
- Tên agent, vị trí cổng duyệt và các công cụ là đề xuất, chưa chốt.

## Câu hỏi còn mở

- Prompt sống ở registry (Langfuse) hay trong git? Registry cho phép sửa và rollback nhanh nhưng bỏ qua code review; git ngược lại. Đề xuất: registry được, nhưng chuyển nhãn `production` chỉ qua cổng eval và người duyệt, nhãn được bảo vệ.
- Ngưỡng của từng tính năng (pass^k với k bao nhiêu, chênh lệch bao nhiêu thì là hồi quy) do dự án đặt; pack chỉ nên có cách tính, không có con số mặc định.
- Ai là "chuyên gia sản phẩm" gán nhãn ở một dự án nhỏ, và bao nhiêu giờ mỗi tuần.
- Có tách voice agent thành domain riêng không, khi phần âm thanh (ASR, TTS, ngắt lời) có vòng kiểm chứng khác hẳn?
