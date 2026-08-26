# Kiến trúc hệ thống P-102

`docs/guide_cho_ca_nhom/data_flow.md` là nguồn sự thật cho workflow nghiệp vụ. Tài liệu này mô tả cấu trúc triển khai hiện hành.

## Dependency direction

```text
Presentation ──> Application ──> Domain
                      │
                      └── ports <── Infrastructure adapters
```

- Domain chứa entity, value object, invariant thuần và repository interface.
- Application chứa use case, workflow, transaction boundary và outbound Agent/validation ports.
- Infrastructure hiện thực persistence, parser, storage, Agent, LLM provider, PII, validation và sandbox.
- Presentation ánh xạ HTTP/DTO, xác định actor và tạo dependency graph; không điều phối nghiệp vụ.
- Infrastructure không import Presentation. Domain không phụ thuộc framework, LLM SDK hoặc parser DBML.

## Data Warehouse workflow

Workflow là chuỗi operation xác định tại Application, không phải graph hay autonomous agent:

```text
Save input
   │
   ├─ requirement changed ──> RequirementAgent.clarify_requirements (1 ainvoke/turn)
   │
   ├─ confirmed requirement changed
   │       └────────> RequirementAgent.derive_analytical_requirements (1 ainvoke)
   │
   ├─ requirement / analytical / source revision changed
   │       └────────> RequirementAgent.evaluate_source_coverage (1 ainvoke)
   │
   └─ READY_FOR_DESIGN ─> DWDesignAgent.generate (1 ainvoke/attempt)
                            │
                      Validation Engine
                            │ ERROR, tối đa 3 attempt
                            └─> DWDesignAgent.revise
```

`SchemaMetadata` profile chỉ đến từ parser/profiler. USER confirmation được lưu riêng dưới dạng typed semantic annotation trên column/relationship; LLM không được ghi annotation này. Không có SourceDataAgent, supervisor, planner, ReAct, tool loop hoặc retry nội bộ. Một Agent operation luôn tương ứng đúng một `ainvoke()`.

Application không giữ transaction database trong lúc gọi LLM. Input revisions được đọc trước; sau invocation, use case mở transaction mới và chỉ persist khi các revision chưa đổi.

## Agent contracts

- `IRequirementAnalysisAgent.clarify_requirements`: raw text/documents/conversation thành BUSINESS/ANALYTICAL/TECHNICAL Requirements và hỏi khi business semantics chưa rõ.
- `IRequirementAnalysisAgent.derive_analytical_requirements`: Requirements đã rõ thành AnalyticalRequirements, không nhận source và không làm yếu Requirement.
- `IRequirementAnalysisAgent.evaluate_source_coverage`: đối chiếu AnalyticalRequirements với SchemaMetadata thành `SUPPORTED`, `NEEDS_SOURCE_CONFIRMATION` hoặc `MISSING_SOURCE`; candidate reference được hậu kiểm deterministic.
- `IDataWarehouseDesignAgent.generate`: thiết kế snapshot đầu tiên từ toàn bộ context.
- `IDataWarehouseDesignAgent.revise`: tạo revision từ Requirements, AnalyticalRequirements, SchemaMetadata, Current DBML, optional user prompt và lỗi validation của attempt trước.
- `IDataModelValidationEngine.validate`: parse DBML và chạy registry rule xác định.

Infrastructure dùng một structured invoker chung để che PII, gọi provider, parse typed output,
hoàn nguyên placeholder và dịch lỗi thành `InfrastructureException`. Mỗi logical invocation có thể
failover tối đa một lần trên từng configured key slot; việc này độc lập với Agent retry.

## LLM provider registry

Agent chỉ nhận structured chat-model protocol lazy; không biết provider hoặc key pool cụ thể. Registry tích hợp sẵn:

- `openai`: OpenAI API.
- `openai_compatible`: OpenRouter hoặc endpoint local tương thích OpenAI.
- `google`: Gemini qua `langchain-google-genai`.

Provider mới được thêm bằng builder đăng ký trong registry. Mỗi key có một client được cache và
reuse; model chính và summary model dùng chung một async-safe key pool theo process. SDK automatic
retry bị tắt cho Agent. Endpoint không dùng AI không yêu cầu API key; Data Model validation luôn
deterministic và không gọi LLM.

`LLM_API_KEYS` là JSON array được ưu tiên. `LLM_API_KEY`, rồi biến OpenAI/Google cũ, chỉ là fallback
tương thích khi key list mới không được khai báo. Key lỗi xác thực/quota bị disable trong RAM; rate
limit chỉ bị bỏ qua trong invocation hiện tại. Log dùng slot 0-based và không chứa secret. Backend
không tự sửa `.env`; thay key rồi restart/redeploy để dựng pool mới.

## Revision và outdated state

Analytical derivation chỉ outdated khi Requirement đổi. Source Coverage outdated khi Requirement/Analytical Requirement hoặc `source_revision` đổi; `covered_analytical_requirement_revision` phân biệt hai trục này. Coverage bị block vẫn được persist và có thể current. Các câu trả lời Source Confirmation được persist độc lập trong một stable batch; chỉ thao tác recheck mới materialize scoped USER annotations, tăng `source_revision` đúng một lần cho cả batch và chạy lại Source Coverage.

Data Model giữ hai generated revisions. Model là outdated khi chúng không khớp analyzed revisions hiện tại. Proposal chỉ giữ model `base_revision`; proposal chỉ `CONFLICTED` khi revision này lệch snapshot hiện hành. Tất cả cờ outdated là derived output, không được persist.

`GET /projects/{project_id}/analysis-status` và `GET /projects/{project_id}/source-coverage` chỉ đọc state. Item resolution dùng `POST /projects/{project_id}/source-coverage/{assessment_id}/resolution` với source/item optimistic revisions và không gọi LLM. `POST /projects/{project_id}/source-coverage/recheck` chỉ chạy khi mọi confirmation item đã được xử lý và gọi đúng Source Coverage operation một lần.

## Data Model và Human Review

- `POST /data-model/generate` chỉ tạo model đầu tiên và trả conflict nếu model đã tồn tại.
- Editor thủ công cập nhật trực tiếp snapshot bằng optimistic revision và không tạo proposal.
- Update Data Model hoặc AI revision tạo `DataModelChange(PROPOSED)`; snapshot AI không đổi trước Accept. Accept hợp lệ tăng revision và ghi nhận analyzed revisions hiện hành; Reject giữ nguyên snapshot.
- Một actor có tối đa một active proposal trên một Data Model; proposal mới thay nội dung active proposal hiện có.
- Update proposal từ context mới chỉ chạy khi Requirement/Analytical analysis đã current.

## Validation

PyDBML parser nằm tại Infrastructure. Validation registry hiện kiểm tra:

- cú pháp DBML;
- duplicate table, column và relationship;
- table/column/reference tồn tại;
- primary key hoặc grain tối thiểu;
- warning thiết kế rule-based có căn cứ.

Chỉ `ERROR` kích hoạt retry hoặc chặn persistence. `WARNING` dành cho hiển thị và không tự thay đổi DBML.

## Persistence và transaction

SQLAlchemy async repositories hiện thực Domain interfaces. `SqlAlchemyUnitOfWork` sở hữu commit/rollback; FastAPI session dependency chỉ cấp phát và đóng session. Repository dịch SQLAlchemy exception thành `InfrastructureException`, ngoại trừ unique active proposal được ánh xạ thành business conflict.

Migration `20260821_replace_workflow_fingerprints_with_revisions.sql` thêm revision columns và xóa các fingerprint columns bằng thay đổi tiến tới.

## PII, storage và sandbox

- Microsoft Presidio analyzer/anonymizer và recognizer registry bảo vệ text trước LLM; policy và language configuration nằm ngoài core service.
- Local storage hiện thực trực tiếp Application file-store ports, dùng resolved-path containment và đưa recursive deletion sang worker thread.
- Sandbox dùng SQLGlot để chỉ chấp nhận PostgreSQL DDL an toàn, bảo vệ `public`, chặn DML/catalog/cross-schema và giữ rollback log.

## API và UI flow

- Project chưa có model: Save & Analyze lưu input, chạy initial workflow rồi mở Modeling.
- Project đã có model: Save & Analyze chỉ chạy Analyze Changes.
- Source upload/update/delete chỉ parse/profile, tăng `source_revision`; không gọi Agent.
- Project Init dùng readiness chung: `REQUIREMENT_CLARIFICATION_REQUIRED`, `SOURCE_CONFIRMATION_REQUIRED`, `SOURCE_DATA_REQUIRED`, `READY_FOR_DESIGN`. Chỉ trạng thái cuối được gọi DWDesignAgent.
- Modeling hiển thị outdated banner. Update Data Model bằng AI mở diff để Accept/Reject; Save DBML thủ công cập nhật trực tiếp snapshot.

OpenAPI client được sinh từ FastAPI schema; không chỉnh tay file generated.

## Conversation Context Management

`session_events` là persistent audit history đầy đủ; LLM context là một projection có giới hạn,
không phải hệ thống history thứ hai. Production session flow không dùng LangGraph. Mỗi invocation
nhận operation-projected canonical project state, cumulative structured summary, explicit pending
clarification, recent completed turns và current input theo nguyên tắc
`Canonical State > Summary > Raw History`.

Canonical projection giữ các business/structural field cần cho operation, loại profiling, sample và
tool payload. Current DBML luôn ở dạng parser/serializer-normalized lossless. Khi source context lớn,
projection ưu tiên các reference active và giữ compact catalog cho phần còn lại. Projector chạy trước
token allocator; summary không được dùng để phục hồi canonical semantics bị project sai.

Summary chỉ lưu conversational state và canonical reference ID/name, không sao chép Requirements,
Analytical Requirements, Schema Metadata hoặc DBML. Pending clarification là workflow state độc lập.
Compaction cumulative chạy đồng bộ ngoài transaction theo checkpoint, persist dưới row lock và bỏ kết
quả stale nếu checkpoint đã thay đổi. Raw events không bị xóa nên vẫn dùng được cho audit/regeneration.

Allocator dành system/output reserve trước, sau đó bảo vệ current input, pending/active state,
required canonical context và bounded summary. Recent history bị drop đầu tiên theo nguyên oldest
completed turn; không cắt giữa turn hoặc mandatory string. Prompt render theo stable-prefix order:
system rules → canonical context → summary → pending state → recent turns → current input. Metrics chỉ
ghi token/count/projection tier, không ghi raw prompt.

Mặc định giữ 6 completed turns và compact batch 4 khi có 10 turns kể từ checkpoint. Đây là engineering
default có cấu hình, không phải scientific optimum, quy tắc “7 ± 2”, hay biện pháp duy nhất cho hiện
tượng “Lost in the Middle”.

## Kiểm thử bắt buộc

- Agent operation: đúng một `ainvoke`, không graph/tool/planner.
- Workflow/revision/concurrency/Human Review/provider registry.
- Repository, transaction, storage, parser, validation và import smoke.
- `ruff check backend/src tests`, toàn bộ `pytest` với `DEBUG=false`, `compileall`.
- Frontend lint, Vitest, production build và OpenAPI regeneration.
