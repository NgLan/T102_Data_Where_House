# Kế hoạch refactor Multi-Provider LLM Gateway

## 1. Mục tiêu và nguyên tắc triển khai

Refactor hệ thống LLM hiện tại từ mô hình một provider/một key pool thành gateway đa provider có:

- thứ tự provider được quyết định hoàn toàn bằng configuration;
- nhiều credential độc lập cho mỗi provider;
- round-robin, cooldown key bị rate limit và disable key không hợp lệ;
- fallback sang provider kế tiếp chỉ với lỗi hạ tầng phù hợp;
- provider health/cooldown đơn giản theo process;
- Agent chỉ phụ thuộc gateway contract, không biết provider, SDK hoặc credential;
- startup validation fail-fast và tuyệt đối không làm lộ secret.

Mọi thay đổi phải tuân theo `docs/guide_cho_ca_nhom/TECHNICAL_CODING_GUIDELINES.md`, đặc biệt:

- file/class/function theo SRP, không quá 25 dòng logic mỗi function, 3 tham số và 120 dòng logic mỗi file;
- Domain/Application không import LangChain hoặc SDK provider;
- lỗi SDK được dịch thành `InfrastructureException` và giữ chain bằng `raise ... from exc`;
- dùng `get_logger(__name__)`, structured `extra` và không log prompt, response đầy đủ hoặc secret;
- không sửa public REST/OpenAPI contract;
- bảo toàn các thay đổi đang staged trong `failure_classifier.py`, `rotating_chat_model.py`,
  `lazy_chat_model.py` và structured-output pipeline hiện tại.

## 2. Hiện trạng và kiến trúc đích

### 2.1. Hiện trạng

- `runtime_configuration.py` resolve đúng một `llm_provider`, một model và một danh sách key.
- `LlmApiKeyPool` dùng chung giữa main/summary model nhưng chỉ có `ACTIVE` và
  `DISABLED_FOR_PROCESS`; rate limit chưa có cooldown theo thời gian.
- `RotatingChatModel` chỉ thử các key của một provider. Timeout, connection error và 5xx chưa
  route sang provider khác.
- `ChatModelProviderRegistry` đang chứa cả registry và builder OpenAI/Gemini trong cùng file.
- Agent đã nhận `StructuredChatModel` protocol lazy, vì vậy có thể thay implementation bên dưới
  mà không đổi Application Agent ports.
- Auto-detection hiện chỉ xử lý prefix OpenRouter trong runtime configuration, chưa phải một
  component độc lập.

### 2.2. Kiến trúc đích

```text
Application workflow
        ↓ Agent port
Infrastructure Agent
        ↓ ILLMGateway
LLMGateway
        ├── ProviderRoutingPolicy
        ├── ProviderHealthRegistry
        └── ProviderRegistry
                  ↓
             ILLMProvider
                  ↓
        OpenAI / Gemini / Anthropic adapter
                  ↓
          CredentialPool của provider
```

Hai quyết định phải độc lập:

1. `ProviderRoutingPolicy` quyết định provider/model candidate theo thứ tự cấu hình.
2. `CredentialPool` quyết định credential nào được dùng trong provider đã chọn.

Không tạo một subsystem song song với `RotatingChatModel`; implementation cũ được refactor và
gỡ bỏ sau khi toàn bộ import/test đã chuyển sang gateway.

## 3. Quyết định cấu hình và backward compatibility

### 3.1. Provider và model

Canonical provider names:

- `OPENAI`
- `GEMINI`
- `ANTHROPIC`

Alias migration:

- `google` được normalize thành `GEMINI`;
- `openai_compatible` được normalize thành `OPENAI` và tiếp tục dùng custom base URL;
- OpenRouter tiếp tục đi qua OpenAI adapter với base URL/model đã cấu hình.

Configuration mới:

```env
LLM_PROVIDER_PRIORITY=GEMINI,OPENAI,ANTHROPIC

GEMINI_API_KEYS=key1,key2
OPENAI_API_KEYS=key1,key2
ANTHROPIC_API_KEYS=key1,key2

GEMINI_MODEL=gemini-model
OPENAI_MODEL=openai-model
ANTHROPIC_MODEL=anthropic-model
```

Các danh sách provider/key chấp nhận CSV như trên và JSON array để tương thích cách khai báo
`LLM_API_KEYS` hiện tại. Sau parse, runtime chỉ dùng typed tuple, không dùng raw string list.

Model summary dùng model base của từng provider nếu không có override. Các override mới là
`GEMINI_SUMMARY_MODEL`, `OPENAI_SUMMARY_MODEL`, `ANTHROPIC_SUMMARY_MODEL`.
`CONVERSATION_SUMMARY_MODEL_NAME` cũ chỉ được migrate khi priority sau normalize có đúng một
provider; nếu có nhiều provider thì startup báo cấu hình mơ hồ thay vì dùng cùng model name cho
provider khác.

### 3.2. Precedence credential

1. Key trong `GEMINI_API_KEYS`, `OPENAI_API_KEYS`, `ANTHROPIC_API_KEYS` được gán tường minh và
   không chạy prefix detection.
2. Khi chưa có `LLM_PROVIDER_PRIORITY`, cặp legacy `LLM_PROVIDER + LLM_API_KEYS/LLM_API_KEY`
   được migrate thành một provider candidate và được xem là explicit binding.
3. `LLM_API_KEYS` trong cấu hình multi-provider mới là generic credentials và phải đi qua detector.
4. `GOOGLE_API_KEY` và `OPENAI_API_KEY` đơn được giữ làm legacy fallback cuối cùng cho đúng
   provider tương ứng.
5. Một raw credential xuất hiện ở nhiều nguồn/provider làm startup thất bại; không silently dedupe.

Local/OpenAI-compatible endpoint phải có một credential/placeholder được khai báo tường minh;
không tiếp tục sinh secret `local` hard-code. Ví dụ local có thể cấu hình
`OPENAI_API_KEYS=ollama`.

### 3.3. Prefix detection

`CredentialProviderDetector` nhận danh sách `ProviderKeyPattern` được inject tại composition root.
Default pattern order từ cụ thể đến tổng quát:

1. `sk-ant-` → `ANTHROPIC`
2. `sk-or-v1-` → `OPENAI`
3. `AIza` → `GEMINI`
4. `sk-` → `OPENAI`

Pattern chỉ áp dụng cho generic credentials. Unknown/ambiguous pattern làm startup validation
thất bại; không đoán provider mặc định và không ghi raw key trong message.

### 3.4. Runtime policy settings

Thêm typed settings với default MVP:

- `LLM_CREDENTIAL_COOLDOWN_SECONDS=60`
- `LLM_PROVIDER_FAILURE_THRESHOLD=2`
- `LLM_PROVIDER_COOLDOWN_SECONDS=30`

Giá trị phải dương; failure threshold tối thiểu là 1. Các giá trị này là operational policy,
không chứa provider priority hoặc secret hard-code.

## 4. Các bước implementation

### Bước 1 — Tách typed LLM configuration và startup validation

- Tạo module settings riêng cho LLM để không tiếp tục mở rộng `backend/config.py` đa trách nhiệm.
- Tạo `LLMProvider`, model profile và provider runtime configuration typed; normalize alias đúng
  một nơi.
- Thay `resolve_runtime_configuration()` một-provider bằng resolver trả ordered provider
  candidates và credential groups.
- Validation tối thiểu: priority không rỗng/trùng; provider đã đăng ký; provider có model;
  credential không rỗng/trùng; generic key detect được; có ít nhất một provider usable.
- Shape/format errors dùng Pydantic validation. Registry/composition errors dùng
  `InfrastructureException(ErrorCode.LLM_ERROR, safe_message)`; không thêm HTTP status vào lỗi.
- Trong FastAPI lifespan, validate và dựng shared gateway runtime trước khi init DB/yield để lỗi
  cấu hình LLM fail-fast lúc startup.

### Bước 2 — Tạo credential model, pool và detector

- Thay raw `SecretStr` tuple bằng `ApiCredential` thuộc Infrastructure gồm `key_id`, `provider`,
  `secret`, `status`, `cooldown_until`, `consecutive_failures`.
- Trạng thái là `AVAILABLE`, `COOLDOWN`, `DISABLED`; `key_id` dạng `openai_01`, không chứa hash,
  prefix, suffix hoặc bất kỳ phần secret nào.
- `CredentialPool` thuộc một provider, async-safe bằng `asyncio.Lock` và dùng clock inject được;
  timestamp hệ thống mặc định lấy từ `utc_now()`.
- Cursor round-robin tiến lên khi acquire thành công. Mỗi logical provider attempt giữ tập
  `attempted_key_ids` để không thử lại cùng credential.
- Success reset `consecutive_failures`; 429 đặt cooldown; authentication/quota-invalid disable;
  credential hết cooldown tự trở lại `AVAILABLE` khi acquire tiếp theo.
- Detector và pool ở file riêng; xóa `api_key_pool.py` sau khi factory/tests đã migrate.

### Bước 3 — Tách provider adapters và registry

- Định nghĩa `ILLMProvider` contract nhận provider-neutral client configuration và credential,
  trả `BaseChatModel` đã tắt SDK retry.
- Tạo adapter riêng cho OpenAI, Gemini và Anthropic; chỉ các file này được import SDK tương ứng.
- `ProviderRegistry` chỉ register/lookup adapter, expose supported providers phục vụ startup
  validation và không chứa branching `if provider`.
- OpenAI adapter hỗ trợ official API, OpenRouter và local/OpenAI-compatible base URL thông qua
  typed configuration; không tự đoán model theo tên.
- Thêm và pin `langchain-anthropic` trong `requirements.txt` theo cùng policy version hiện có.
- Catch lỗi khởi tạo SDK cụ thể, dịch sang `InfrastructureException` với safe message và
  `raise ... from exc`.

### Bước 4 — Chuẩn hóa failure classification và provider health

Failure classifier trả một decision typed gồm action, safe reason và `ErrorCode`:

| Lỗi | Credential action | Provider action |
|---|---|---|
| 429/rate limit | `COOLDOWN` key | thử key tiếp theo; hết key thì fallback |
| 401/403/invalid credential | `DISABLED` key | thử key tiếp theo; hết key thì fallback |
| quota/billing invalid cho key | `DISABLED` key | thử key tiếp theo; hết key thì fallback |
| timeout/connection/5xx | không đổi key | ghi provider failure và fallback ngay |
| provider đang cooldown | không acquire key | bỏ qua provider |
| model 404/configuration error | không đổi key | fail operation, không che lỗi bằng fallback |
| JSON/Pydantic/structured/semantic/business validation | không đổi key | fail operation, không fallback |

- Provider health gồm `AVAILABLE`, `COOLDOWN`, failure count và `cooldown_until`.
- Timeout/connection/5xx của một invocation làm fallback ngay. Khi failure count liên tiếp đạt
  threshold, provider chuyển cooldown để invocation sau bỏ qua nhanh.
- Provider success reset failure count/health. Credential failures không tăng provider-level 5xx
  counter; provider hết usable credential vẫn được fallback trong invocation hiện tại.
- Không dựa vào raw exception message nếu SDK type/status có sẵn. Fallback message matching chỉ
  là compatibility path, không đưa raw message vào log/response.

### Bước 5 — Xây LLMGateway và giữ Agent provider-neutral

- Tạo `ILLMGateway`/structured-call protocol tương đương contract hiện tại và lazy wrapper riêng.
- Gateway duyệt ordered candidates từ routing policy, kiểm tra provider health, rồi giao việc
  chọn key cho pool của provider.
- Gateway không parse business output. Structured-output decoder/retry hiện tại tiếp tục nằm ở
  Agent/structured invoker layer và chỉ chủ động tạo invocation mới theo retry policy của operation.
- Chỉ dịch lỗi cuối cùng sau khi route hợp lệ đã cạn; exception trả ra dùng các `ErrorCode.LLM_*`
  hiện có để giữ API contract.
- Main và summary gateway là hai model profile nhưng chia sẻ cùng credential pools và provider
  health registry theo process.
- Migrate toàn bộ Agent source từ `StructuredChatModel`/`LazyChatModel` sang gateway protocol;
  xóa rotating implementation/alias cũ khi không còn import.

### Bước 6 — Composition root, health và observability

- Factory Infrastructure chỉ dựng registry/runtime/gateway resources; process cache và wiring
  Agent đặt tại dependency composition hiện có.
- Cập nhật các dependency của Requirement, Data Warehouse và Conversation Summary để inject
  cached gateway/profile, không instantiate provider trong Application Service hoặc Agent.
- Health dependency đọc validated runtime: healthy khi có ít nhất một provider candidate không
  cooldown và có usable credential; không expose key count/status chi tiết qua REST.
- Structured log events:
  - `llm_provider_selected`
  - `llm_model_selected`
  - `llm_key_rotated`
  - `llm_provider_fallback`
  - `llm_provider_cooldown`
  - `llm_call_failed`
- Log fields chỉ gồm provider, model, anonymous `key_id`, attempt, safe reason, latency và token/
  finish metadata đã có. Không log raw SDK exception, prompt, response, authorization hoặc secret.
- Giữ provider/model/finish metadata từ structured raw response; khi SDK thiếu provider/model,
  dùng route metadata đã biết của gateway, không suy ra từ credential.

### Bước 7 — Migration tài liệu và cleanup

- Cập nhật `.env.example`, README và `ARCHITECTURE.md` với provider priority, key/model per provider,
  generic detection, rotation/fallback matrix và cách thêm provider mới.
- Ghi rõ thêm/bớt key chỉ cần đổi environment rồi restart/redeploy; runtime không sửa `.env` và
  không persist raw secret.
- Không sửa frontend/OpenAPI vì đây là internal routing refactor.
- Nếu implementation thật sự cần `ErrorCode` mới, phải đồng thời cập nhật `error_status.py`,
  `frontend/src/common/i18n/locales/{vi,en}/errors.json` và exhaustiveness tests. Mặc định plan
  tái sử dụng error codes LLM hiện có.
- Sau khi mọi test đã migrate, xóa file/class cũ không còn dùng; không giữ adapter/gateway legacy
  chạy song song.

## 5. Kế hoạch test và tiêu chí chấp nhận

### 5.1. Configuration và detector

1. Provider được duyệt đúng thứ tự `LLM_PROVIDER_PRIORITY`.
2. Đổi priority bằng environment làm đổi route mà không sửa source.
3. Priority rỗng/trùng hoặc provider chưa register làm startup fail.
4. Provider được enable nhưng thiếu model/credential làm startup fail.
5. Explicit provider keys không chạy detector và thắng prefix không khớp.
6. Generic key được detect đúng với Gemini/OpenAI/Anthropic/OpenRouter patterns.
7. Unknown hoặc ambiguous prefix làm configuration validation fail mà không chứa key trong lỗi.
8. Legacy single-provider configuration vẫn resolve đúng theo precedence đã định.

### 5.2. Credential pool

9. N key được chọn round-robin qua nhiều invocation.
10. Key 429 chuyển cooldown và key kế tiếp được chọn.
11. Key hết cooldown được dùng lại.
12. Authentication/quota-invalid disable key cho tới khi process restart.
13. Late concurrent success không reactivate key đã disabled/cooldown bởi coroutine khác.
14. Concurrent acquire/state update không làm hỏng cursor hoặc provider ownership.

### 5.3. Gateway, failure và health

15. Hết usable key provider A fallback provider B.
16. Timeout/connection/5xx fallback ngay mà không thử tuần tự mọi key provider A.
17. Provider failure đạt threshold chuyển cooldown; invocation sau bỏ qua A.
18. Provider success reset health counter.
19. Model-not-found fail operation và không rotate/fallback.
20. Structured JSON/Pydantic/semantic validation không đổi key/provider health và không fallback.
21. Agent structured-output retry chủ động gọi gateway lần mới nhưng key trước đó vẫn available.
22. Tất cả provider fail trả `InfrastructureException/ErrorCode` chuẩn và giữ exception chain.

### 5.4. Security, metadata và regression

23. Raw secret và partial secret không xuất hiện trong log, exception, repr, Agent result hoặc
    session event; kiểm tra bằng `caplog` với sentinel secret.
24. Log rotation/fallback chỉ dùng anonymous `key_id` và safe reason.
25. Provider/model/latency/token/finish metadata được ghi nhận đúng cho provider thực sự thành công.
26. Main/summary gateway dùng chung credential/health state nhưng đúng model profile.
27. Agent/Application import-boundary tests xác nhận không import OpenAI/Google/Anthropic SDK.
28. REST/OpenAPI contract tests hiện tại không thay đổi.

### 5.5. Verification cuối

Chạy theo thứ tự:

```bash
# Targeted tests trong quá trình refactor
pytest tests/test_agents/test_llm_configuration.py
pytest tests/test_agents/test_api_key_pool.py
pytest tests/test_agents/test_provider_registry.py
pytest tests/test_agents/test_llm_failure_classifier.py
pytest tests/test_agents/test_rotating_chat_model.py
pytest tests/test_agents/test_llm_factory_lifecycle.py

# Theo coding guidelines, từ backend working directory phù hợp
ruff check src/ tests/
pytest
```

Sau test, chạy guideline/import compliance suites hiện có và rà thủ công:

- function không quá 25 dòng logic và tối đa 3 tham số;
- file thủ công không quá 120 dòng logic;
- không có provider branching trong Agent/Application;
- không có raw `datetime.now()`, `print()`, secret logging hoặc SDK exception leak;
- không có file gateway/key-rotation cũ chạy song song.

## 6. Báo cáo bắt buộc sau implementation

Báo cáo kết quả phải gồm:

1. Kiến trúc trước và sau refactor.
2. File được thêm/sửa/xóa, tách riêng thay đổi staged có sẵn được bảo toàn.
3. Vị trí và ví dụ cấu hình provider priority.
4. Cách thêm provider adapter/pattern/model mới.
5. Cách thêm/bớt key chỉ bằng environment.
6. Precedence và cách prefix detector hoạt động.
7. Ma trận lỗi rotate key, fallback provider và tuyệt đối không rotate.
8. Provider health/cooldown lifecycle.
9. Các test đã thêm/cập nhật và kết quả Ruff/Pytest.
10. Xác nhận REST/OpenAPI contract và secret-handling không thay đổi.
