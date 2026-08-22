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
   ├─ raw changed ──> RequirementAgent.structure_raw_requirement (1 ainvoke)
   │
   ├─ requirement/schema changed
   │       └────────> RequirementAgent.derive_analytical_requirements (1 ainvoke)
   │
   └─ initial model ─> DWDesignAgent.generate (1 ainvoke/attempt)
                            │
                      Validation Engine
                            │ ERROR, tối đa 3 attempt
                            └─> DWDesignAgent.revise
```

`SchemaMetadata` chỉ đến từ parser/profiler. Không có SourceDataAgent, supervisor, planner, ReAct, tool loop hoặc retry nội bộ. Một Agent operation luôn tương ứng đúng một `ainvoke()`.

Application không giữ transaction database trong lúc gọi LLM. Input revisions được đọc trước; sau invocation, use case mở transaction mới và chỉ persist khi các revision chưa đổi.

## Agent contracts

- `IRequirementAnalysisAgent.structure_raw_requirement`: raw text thành BUSINESS/ANALYTICAL/TECHNICAL Requirements.
- `IRequirementAnalysisAgent.derive_analytical_requirements`: Requirements và SchemaMetadata thành AnalyticalRequirements có `source_requirement_id` chính xác.
- `IDataWarehouseDesignAgent.generate`: thiết kế snapshot đầu tiên từ toàn bộ context.
- `IDataWarehouseDesignAgent.revise`: tạo revision từ Requirements, AnalyticalRequirements, SchemaMetadata, Current DBML, optional user prompt và lỗi validation của attempt trước.
- `IDataModelValidationEngine.validate`: parse DBML và chạy registry rule xác định.

Infrastructure dùng một structured invoker chung để che PII, gọi provider đúng một lần, parse typed output, hoàn nguyên placeholder và dịch lỗi thành `InfrastructureException(LLM_ERROR)`.

## LLM provider registry

Agent chỉ nhận `BaseChatModel` lazy; không biết provider cụ thể. Registry tích hợp sẵn:

- `openai`: OpenAI API.
- `openai_compatible`: OpenRouter hoặc endpoint local tương thích OpenAI.
- `google`: Gemini qua `langchain-google-genai`.

Provider mới được thêm bằng builder đăng ký trong registry. Model được cache theo process và SDK automatic retry bị tắt cho Agent. Endpoint không dùng AI không yêu cầu API key; Data Model validation luôn deterministic và không gọi LLM.

Các biến cấu hình chính là `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_BASE_URL`, `MODEL_NAME`; các biến OpenAI/Google cũ chỉ là fallback tương thích.

## Revision và outdated state

Project giữ `requirement_revision`, `source_revision` và hai analyzed revision tương ứng. Save Requirement hoặc thay đổi nội dung source tăng revision đầu vào. `Analyze Changes` chỉ cập nhật analyzed revisions sau khi các Agent operation cần thiết thành công.

Data Model giữ hai generated revisions. Model là outdated khi chúng không khớp analyzed revisions hiện tại. Proposal chỉ giữ model `base_revision`; proposal chỉ `CONFLICTED` khi revision này lệch snapshot hiện hành. Tất cả cờ outdated là derived output, không được persist.

`GET /projects/{project_id}/analysis` chỉ đọc trạng thái. `POST` cùng path chạy operation cần thiết; input không đổi thì không gọi LLM.

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
- Modeling hiển thị outdated banner. Update Data Model bằng AI mở diff để Accept/Reject; Save DBML thủ công cập nhật trực tiếp snapshot.

OpenAPI client được sinh từ FastAPI schema; không chỉnh tay file generated.

## Kiểm thử bắt buộc

- Agent operation: đúng một `ainvoke`, không graph/tool/planner.
- Workflow/revision/concurrency/Human Review/provider registry.
- Repository, transaction, storage, parser, validation và import smoke.
- `ruff check backend/src tests`, toàn bộ `pytest` với `DEBUG=false`, `compileall`.
- Frontend lint, Vitest, production build và OpenAPI regeneration.
