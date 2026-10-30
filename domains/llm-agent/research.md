# Nghiên cứu nền cho domain `llm-agent` (2026-10)

Ghi chú nghiên cứu làm căn cứ cho [README](README.md) và các sơ đồ của gói. Mỗi ý có nguồn; **[chưa kiểm]** là ý chỉ có nguồn thứ cấp, nguồn của chính nhà bán, hoặc là suy luận. Tên model, giá và lịch ngừng hỗ trợ ghi theo ngày tra 2026-10-29 và sẽ cũ nhanh.

## 1. Eval

### 1.1. Bắt đầu từ phân tích lỗi, không từ chỉ số

- Đọc trace thật, ghi nhận xét tự do cho từng trace (open coding), rồi gom thành phân loại lỗi (axial coding). Tự gán nhãn ít nhất 30 trace trước khi để LLM gợi ý; đọc tiếp tới khi không còn dạng lỗi mới ([Hamel Husain](https://hamel.dev/blog/posts/evals-faq/)).
- Người gán nhãn đầu tiên phải là chuyên gia của sản phẩm, không giao cho LLM vì LLM thiếu ngữ cảnh sản phẩm; một người quyết về chất lượng ("benevolent dictator"), xem 10–20 trace mỗi tuần (cùng nguồn).
- Bộ eval đầu tiên chỉ cần 20–50 ca lấy từ lỗi thật, có đáp án tham chiếu, cân bằng ca "nên làm" và "không nên làm". Pass rate 0% qua nhiều lần chạy thường là ca hỏng chứ không phải agent hỏng ([Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)).

### 1.2. Chấm điểm

- Thứ tự: kiểm bằng code (assert, regex, trạng thái) trước, LLM judge chỉ cho chỗ cần phán đoán, người để hiệu chỉnh. Chấm kết quả chứ không chấm đường đi (Anthropic, như trên).
- Mỗi dạng lỗi một judge nhị phân, thay vì một judge "chất lượng" thang Likert. Hiệu chỉnh judge trên 100–200 nhãn người cho mỗi dạng lỗi, chia train/dev/test, báo TPR/TNR so với nhãn người ([Hamel Husain](https://hamel.dev/blog/posts/evals-faq/), [OpenAI](https://developers.openai.com/api/docs/guides/evaluation-best-practices)).
- Judge có thiên lệch vị trí, độ dài và tự đề cao; judge mạnh đạt hơn 80% đồng thuận với người, ngang mức người với người ([Zheng et al.](https://arxiv.org/abs/2306.05685)). So cặp tốt hơn chấm điểm cho tiêu chí chủ quan; chấm trực tiếp tốt hơn cho tiêu chí khách quan như vi phạm chính sách ([Eugene Yan](https://eugeneyan.com/writing/llm-evaluators/)).

### 1.3. Kết quả dao động

- pass@k: ít nhất một lần thành công trong k lần; pass^k: cả k lần đều thành công, là chỉ số đúng cho độ ổn định với người dùng. 0,75 mỗi lần cho pass^3 ≈ 0,42 ([Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), [τ-bench](https://arxiv.org/abs/2406.12045)).
- Mỗi lần chạy bắt đầu từ môi trường sạch. So hai phiên bản bằng hiệu số theo từng ca (paired), gom sai số theo hội thoại khi các lượt tương quan; sai số gom có thể lớn hơn 3 lần sai số ngây thơ ([Anthropic](https://www.anthropic.com/research/statistical-approach-to-model-evals), [arXiv 2411.00640](https://arxiv.org/abs/2411.00640)).

### 1.4. Agent nhiều lượt và có công cụ

- Chấm trạng thái cuối (dữ liệu, tham số công cụ) so với trạng thái mục tiêu, không so chuỗi hội thoại ([τ-bench](https://arxiv.org/abs/2406.12045), [τ²-bench](https://arxiv.org/abs/2506.07982)).
- Hai pha: đo thành công đầu-cuối, rồi chẩn đoán từng bước (chọn công cụ, tham số, kết quả, trạng thái). Gán nhãn lỗi đầu tiên ở thượng nguồn; "N-1 testing" (phát lại phần đầu hội thoại thật, chỉ sinh lượt kế tiếp) thường tốt hơn người dùng mô phỏng hoàn toàn ([Hamel Husain](https://hamel.dev/blog/posts/evals-faq/)).
- Eval khả năng tách khỏi eval hồi quy: eval khả năng bão hoà thì chuyển sang bộ hồi quy, bộ này phải giữ gần 100% ([Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)).

### 1.5. Agent lập trình tự "lách" eval

- METR thấy model sửa hoặc giả lập bộ chấm, ghi đè đồng hồ, tìm lời giải bị lộ; o3 lách ở 30,4% lần chạy RE-Bench, nhiều hơn khoảng 43 lần khi nhìn thấy hàm chấm; thêm câu "đừng gian lận" vẫn còn 80% lách ([METR](https://metr.org/blog/2025-06-05-recent-reward-hacking/)).
- Thói lách học được lan sang hành vi lệch rộng hơn, kể cả phá mã phát hiện ở 12% lần thử; loại bỏ khả năng lách khỏi môi trường thì hiệu quả ([arXiv 2511.18397](https://arxiv.org/abs/2511.18397)).
- Anthropic tối ưu công cụ bằng Claude Code trên transcript nhưng dựa vào tập held-out để không overfit ([Anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)); bộ tối ưu prompt của promptfoo mặc định overfit toàn tập và khuyên giữ 20% để kiểm ([promptfoo](https://www.promptfoo.dev/docs/usage/prompt-optimization/)).
- Chỉ dẫn trong `CLAUDE.md` không tất định; quy tắc không ngoại lệ phải dựa vào hook, deny rule, CI và branch protection; review diff bằng subagent mới, không bị ảnh hưởng bởi lập luận đã sinh ra code ([Claude Code](https://code.claude.com/docs/en/best-practices)).

## 2. Phát hành

- **Prompt registry**: mỗi phiên bản prompt bất biến; nhãn `production` là bản đang phục vụ; rollback bằng cách chuyển nhãn về bản cũ, không cần đổi code; có nhãn được bảo vệ ([Langfuse](https://langfuse.com/docs/prompt-management/features/prompt-version-control), [LangSmith](https://docs.langchain.com/langsmith/manage-prompts)). Truyền đối tượng prompt vào lời gọi model thì trace gắn với phiên bản prompt; dùng prompt dự phòng thì mất liên kết ([Langfuse](https://langfuse.com/docs/prompt-management/features/link-to-traces)).
- **Chuyển nhãn là một lần triển khai bỏ qua code review.** Hai nhà bán không hướng dẫn chuyện này; đề xuất của gói: chuyển nhãn phải qua cùng bộ eval với thay đổi code, và mọi trace ghi phiên bản prompt, snapshot model, hash cấu hình, commit **[suy luận]**.
- **Cổng trong CI**: action eval đăng chênh lệch điểm theo từng bộ chấm lên PR và chặn merge dưới ngưỡng ([Braintrust](https://braintrust.dev/docs/evaluate/run-in-ci)).
- **Shadow → canary → toàn bộ**: shadow chỉ bắt thay đổi chi phí, độ dài, tỉ lệ từ chối, không đo chất lượng; canary băm theo người dùng để mỗi người ở một phiên bản, có ngưỡng rõ cho từng giai đoạn ([tianpan.co](https://tianpan.co/blog/2026-04-09-llm-gradual-rollout-shadow-canary-ab-testing), thực hành người làm nghề **[chưa kiểm]**).
- **Ngừng hỗ trợ model**: Anthropic báo trước ít nhất 60 ngày, vòng đời Active → Legacy → Deprecated → Retired, gọi model đã retire thì lỗi ([Anthropic](https://platform.claude.com/docs/en/about-claude/model-deprecations)); OpenAI ít nhất 6 tháng với model GA, khoảng 2 tuần với bản preview ([OpenAI](https://developers.openai.com/api/docs/deprecations)); Google báo 2 tuần khi alias `latest` đổi có tính phá vỡ ([Google](https://ai.google.dev/gemini-api/docs/models)). Hệ quả: ghim snapshot có ngày, coi mỗi lần đổi model là một lần phát hành chạy đủ bộ eval.
- **Đổi model kéo theo đổi API và chi phí**: ví dụ hướng dẫn chuyển sang Sonnet 5.5 có thay đổi phá vỡ (không còn ép `tool_choice`), thinking bật mặc định, phải chạy lại eval ở vài mức effort và tính lại chi phí; API `2026-10-21` bỏ `temperature`/`top_p`/`top_k` ([Anthropic](https://platform.claude.com/docs/en/models/sonnet-5-5/migration-guide)).
- **Prompt caching**: thứ tự tiền tố cache là tools → system → messages, sửa định nghĩa tool làm mất cả cache ([Anthropic](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)). Sửa prompt hay tool vì vậy có tác dụng phụ lên chi phí và độ trễ.

## 3. Vận hành, quan sát

- OpenTelemetry GenAI semantic conventions vẫn ở trạng thái Development: span `invoke_agent`, `execute_tool`, thuộc tính `gen_ai.request.model`, `gen_ai.usage.input_tokens`; nội dung tin nhắn chỉ ghi khi bật, vì quyền riêng tư ([OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans)).
- Nền tảng quan sát (Langfuse, Datadog LLM Observability, LangSmith, Braintrust) đều có trace, session, evaluator online trên lưu lượng được lấy mẫu, hàng đợi gán nhãn ([Langfuse](https://langfuse.com/docs/evaluation/evaluation-methods/annotation-queues), [Datadog](https://docs.datadoghq.com/llm_observability/evaluations/managed_evaluations/security_and_safety_evaluations), [Braintrust](https://www.braintrust.dev/docs/core/logs/score)). Langfuse không chạy judge trên cả session vì không biết session kết thúc khi nào ([Langfuse](https://langfuse.com/faq/all/evaluating-sessions-conversations)).
- Chỉ số thường theo dõi (tổng hợp, không phải chuẩn): độ trễ p95 theo model, token và chi phí mỗi phiên, điểm judge, cờ injection và độc hại, tỉ lệ lỗi công cụ, tỉ lệ dự phòng, tỉ lệ không trả lời được.
- Kiểm theo tầng: kiểm tất định rẻ trên mọi trace, judge đắt trên mẫu; theo dõi khoảng tin cậy, điều tra khi cận dưới vượt ngưỡng ([Hamel Husain](https://hamel.dev/blog/posts/evals-faq/)).
- Sự cố: retry cùng nơi, rồi dự phòng sang model khác, có circuit breaker ([LiteLLM](https://docs.litellm.ai/docs/proxy/reliability)); rollback prompt bằng chuyển nhãn, client nhận khi cache prompt làm mới (Langfuse). Không có chuẩn "kill switch"; gói đề xuất gộp: chuyển nhãn, cờ tắt từng công cụ, chặn hành động có hậu quả **[suy luận]**.
- Voice agent: thời gian tới âm thanh đầu tiên tính từ lúc người dùng ngừng nói (gợi ý p95 ≤ 800 ms), độ trễ endpointing, tỉ lệ ngắt lời đúng/sai; WER chỉ đo phần ASR ([Hamming](https://hamming.ai/blog/how-to-evaluate-voice-agents-2026), ngưỡng của nhà bán **[chưa kiểm]**). Pipecat Evals có chế độ âm thanh bắt được lỗi ngắt lời mà test văn bản bỏ sót, thoát 0/1 nên chạy được trong CI ([Pipecat](https://docs.pipecat.ai/pipecat/evals/overview)). Timestamp phía server bỏ qua thời gian mạng ([Telnyx](https://telnyx.com/resources/how-to-evaluate-voice-ai-the-way-real-conversations-work.md)).

## 4. An toàn

- OWASP Top 10 cho ứng dụng LLM 2025: prompt injection, lộ thông tin nhạy cảm, chuỗi cung ứng, đầu độc dữ liệu, xử lý đầu ra sai, quyền quá mức (excessive agency), lộ system prompt, điểm yếu vector, thông tin sai, tiêu thụ không giới hạn ([promptfoo](https://www.promptfoo.dev/docs/red-team/owasp-llm-top-10/)). OWASP Top 10 cho ứng dụng agent 2026: chiếm mục tiêu agent (thường qua injection gián tiếp), lạm dụng công cụ, agent mất kiểm soát ([Cycode](https://cycode.com/blog/owasp-top-10-agentic-applications/)).
- Injection gián tiếp: đánh dấu văn bản từ nguồn không tin cậy (spotlighting) giảm tỉ lệ tấn công thành công từ hơn 50% xuống dưới 2% trong thử nghiệm của Microsoft ([Microsoft Research](https://www.microsoft.com/en-us/research/?p=1124166)); ở mức kiến trúc, đầu vào không tin cậy không được kích hoạt hành động có hậu quả ([arXiv 2506.08837](https://arxiv.org/abs/2506.08837)).
- Công cụ xếp hạng rủi ro theo đọc/ghi, hoàn tác được không, quyền cần, ảnh hưởng tài chính; hành động rủi ro cao cần người xác nhận ([OpenAI](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf), qua bản tóm tắt **[chưa kiểm]**).
- Red team: garak (bộ probe cố định), PyRIT (LLM tấn công nhiều lượt), promptfoo (chạy trong CI); nên kết hợp ([promptfoo](https://www.promptfoo.dev/blog/promptfoo-vs-garak/)). NIST AI 600-1 liệt kê 12 rủi ro của AI tạo sinh, tự nguyện ([NIST](https://doi.org/10.6028/NIST.AI.600-1)).

### 4.1. Trẻ em và dữ liệu cá nhân

| Quy định | Điểm liên quan | Nguồn |
| --- | --- | --- |
| COPPA (sửa đổi 2025) | hạn tuân thủ đầy đủ 22/4/2026; cần đồng ý riêng của cha mẹ trước khi chia sẻ dữ liệu trẻ cho bên thứ ba | [Hunton](https://www.hunton.com/privacy-and-cybersecurity-law-blog/coppa-rule-amendment-compliance-deadline-approaches) |
| FTC 6(b) (9/2025) | hỏi các hãng chatbot về thử nghiệm tác hại, giới hạn với trẻ vị thành niên, dữ liệu an toàn theo độ tuổi | [DLA Piper](https://www.dlapiper.com/en-sg/insights/publications/2025/09/ftc-ai-chatbots) |
| California SB 243 (hiệu lực 1/1/2026) | chatbot đồng hành phải báo người dùng vị thành niên rằng đang nói chuyện với AI, nhắc lại mỗi 3 giờ, công bố quy trình an toàn | [FPF](https://fpf.org/blog/understanding-the-new-wave-of-chatbot-legislation-california-sb-243-and-beyond/) |
| EU AI Act | cấm AI khai thác điểm yếu do tuổi (Điều 5, từ 2/2025); nghĩa vụ minh bạch là AI (Điều 50) áp dụng từ 2/8/2026 | [5Rights](https://5rightsfoundation.com/ai-systems-that-exploit-the-vulnerabilities-of-children-are-now-illegal-in-the-eu/), [Baker Botts](https://www.bakerbotts.com/thought-leadership/publications/2026/september/eu-ai-act-article-50-transparency-obligations-go-live) |
| Việt Nam: Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15 (hiệu lực 1/1/2026), Nghị định 356/2025 | thay Nghị định 13/2023; đồng ý không được mặc định; quy định rõ về dữ liệu nhạy cảm. Quy tắc trẻ từ 7 tuổi cùng đồng ý với cha mẹ lấy từ Nghị định 13 **[chưa kiểm]** dưới luật mới | [LuatVietnam](https://english.luatvietnam.vn/legal-updates/the-latest-law-on-personal-data-protection-and-the-guiding-documents-892-106778-article.html) |

- Lọc PII trong SDK trước khi trace rời ứng dụng; đặt thời hạn lưu theo dự án ([Langfuse](https://langfuse.com/docs/observability/features/masking), [Langfuse](https://langfuse.com/security/manage-personal-data.md)).
- Sao chép hội thoại vào bộ eval là một bước xử lý dữ liệu riêng, nằm ngoài thời hạn lưu của trace, nên cần cơ sở pháp lý riêng (với trẻ em: đồng ý của cha mẹ) **[suy luận từ các nguồn trên]**.

## 5. Kiến trúc sản phẩm và tri thức mau cũ

- Workflow (đường đi định sẵn) khác agent (LLM tự điều hướng); bắt đầu từ cách đơn giản nhất, chỉ thêm quyền tự chủ khi đo được lợi ích. Năm mẫu: chuỗi prompt, định tuyến, song song, điều phối–thợ, đánh giá–tối ưu ([Anthropic](https://www.anthropic.com/engineering/building-effective-agents)).
- Đồ thị trạng thái hội thoại khai báo được bằng JSON (Pipecat Flows `FlowConfig`) hoặc runtime có trạng thái bền (LangGraph) ([Pipecat](https://docs.pipecat.ai/guides/features/pipecat-flows), [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview)).
- Context là ngân sách chú ý hữu hạn; ít công cụ, không chồng lấn; truy xuất đúng lúc; nén hội thoại dài ([Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). Công cụ: gộp quy trình vào một tool, đặt namespace, lỗi có hướng dẫn sửa, kiểm bằng eval nhiều lượt gọi ([Anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)).
- MCP: bản đặc tả 2026-07-28 ([MCP blog](https://blog.modelcontextprotocol.io/)); số liệu về mức độ dùng chỉ có nguồn thứ cấp **[chưa kiểm]**.
- Tri thức cũ nhanh: tên model, giá, tham số được hỗ trợ, lịch ngừng hỗ trợ, API SDK, cả nền tảng của nhà bán (OpenAI đang bỏ nền tảng Evals hosted, [OpenAI](https://developers.openai.com/api/docs/guides/evaluation-best-practices)). Cách giữ tươi: tra tài liệu qua llms.txt ([llmstxt.org](https://llmstxt.org/)) hoặc MCP tài liệu như Context7 ([Upstash](https://upstash.com/blog/context7-mcp)), ghi ngày tra; ghim phiên bản SDK và snapshot model.

## 6. Hệ quả cho kiến trúc của gói

| Phát hiện | Thay đổi trong gói |
| --- | --- |
| Agent lập trình lách eval khi nhìn thấy bộ chấm; dặn bằng lời không đủ (§1.5) | Tách bộ eval dev (builder đọc được) và held-out đóng băng (chỉ verifier chạy); builder không có quyền ghi bộ eval, judge, held-out, chặn bằng hook/deny rule |
| Phân tích lỗi phải do chuyên gia sản phẩm, judge phải hiệu chỉnh theo nhãn người (§1.1, §1.2) | Bước người gán nhãn trong sơ đồ 02; sơ đồ 04 vòng dữ liệu từ trace tới ca eval và judge đã hiệu chỉnh |
| Kết quả dao động (§1.3) | Bằng chứng dạng chỉ số: pass^k, so cặp, gom theo hội thoại |
| Chuyển nhãn prompt là triển khai ngoài code review (§2) | Sơ đồ 03 vòng đời một phiên bản; chuyển nhãn `production` chỉ sau held-out PASS và người duyệt |
| Model ngừng hỗ trợ theo lịch của nhà cung cấp (§2) | Sự kiện ngoài kích hoạt vòng lặp; trạng thái "chờ di chuyển model" ở sơ đồ 03 |
| Hội thoại thật chứa dữ liệu cá nhân, có khi của trẻ em (§4.1) | Cổng lọc PII và đồng ý trước khi trace thành ca eval (sơ đồ 04) |
| Injection gián tiếp và quyền công cụ (§4) | Red team trong kiểm chứng; công cụ có hậu quả cần người xác nhận |
