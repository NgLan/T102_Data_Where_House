# Quy Định Kỹ Thuật Khi Viết Code (Coding Guidelines)

Tài liệu này tổng hợp toàn bộ các quy định kỹ thuật, kiến trúc và chuẩn mực viết code cho dự án. Mọi thành viên (Backend & Frontend) cần đọc kỹ và tuân thủ nghiêm ngặt trong suốt quá trình phát triển.

---

## 0. QUY TẮC BẮT BUỘC ĐỌC TRƯỚC

Các quy tắc trong mục này có mức ưu tiên cao nhất. Nếu nội dung cũ bên dưới mâu thuẫn, áp dụng mục này.

### 0.1. SRP, DRY và giới hạn kích thước

- **Single Responsibility Principle (SRP):** Một file, class hoặc function chỉ có một lý do để thay đổi. Không đặt DTO, dependency wiring, business logic, persistence và HTTP handling chung một file.
- **Don't Repeat Yourself (DRY):** Mỗi business rule, validation rule, mapping hoặc API contract chỉ có một nguồn sự thật. Tái sử dụng abstraction hiện có; không copy logic giữa Presentation, Application, Domain và Frontend.
- Function/method tối đa **25 dòng logic** và tối đa **3 tham số**. Nếu vượt giới hạn, tách function hoặc gom tham số thành application input model/Pydantic request model phù hợp với layer.
- File code thủ công tối đa **120 dòng logic**. Khi gần giới hạn phải tách theo trách nhiệm, không tách máy móc theo từng method. File generated, migration, lock file và OpenAPI snapshot không áp dụng giới hạn này và không được sửa thủ công.
- Không tạo file chung chung như `helpers.py`, `common_service.py` hoặc `application.py` nếu file chứa nhiều trách nhiệm không liên quan. Tên file phải phản ánh đúng feature hoặc trách nhiệm duy nhất.

### 0.2. Trình tự bắt buộc khi tạo một chức năng Backend

1. **Domain (`src/domain/<module>/`):** Tạo/cập nhật entity, value object, enum và business rule thuần. Nếu cần persistence, khai báo repository interface tại Domain. Domain không import FastAPI, Pydantic, SQLAlchemy hoặc Infrastructure.
2. **Application input/output (`src/application/<module>/input|output/`):** Khai báo input/output model độc lập HTTP. Không dùng Pydantic request DTO làm application input và không trả domain entity qua application boundary.
3. **Application service interface (`i_<module>_service.py`):** Thêm method công khai vào interface service duy nhất của module. Method nhận application input và trả application output.
4. **Application service (`<module>_service.py`):** Hiện thực interface, điều phối domain rule, repository interface và `IUnitOfWork`. Không import concrete repository/ORM/FastAPI. Method hiện thực interface phải dùng `@override` khi runtime hỗ trợ.
5. **Infrastructure (`src/infrastructure/`):** Tạo ORM model, mapper và concrete repository khi cần. Repository phải kế thừa Domain interface, dùng `@override` và giữ nguyên contract về tên/kiểu tham số, kiểu trả về.
6. **Presentation request DTO (`src/presentation/dtos/<module>/request.py`):** Khai báo Pydantic model, `Field` constraints, `field_validator`/`model_validator`, `extra="forbid"` và mapping sang application input. Tất cả kiểm tra hình dạng/định dạng input HTTP phải kết thúc tại đây. Validator DTO chỉ được phát sinh lỗi validation của Pydantic (`ValueError`, `PydanticCustomError` hoặc lỗi constraint); không để `BusinessException`, `HTTPException` hay exception thư viện thoát trực tiếp khỏi validator. Mọi `RequestValidationError` phải đi qua global validation handler duy nhất và trả `details` dạng danh sách, mỗi vị trí field sai là một phần tử `{field, message}`. Domain vẫn phải bảo vệ invariant để chống bypass từ CLI, queue hoặc test.
7. **Presentation response payload DTO (`response.py`):** Chỉ mô tả payload `data`, có type và `Field` metadata đầy đủ để sinh OpenAPI. Mapping application output sang payload được đặt tại đây; không tự tạo success envelope theo module.
8. **Dependency wiring (`src/presentation/dependencies/<module>.py`):** Tạo provider FastAPI `Depends` để nối application service interface với concrete repository/UoW. Đây là composition root duy nhất được phép import cả Application interface và Infrastructure implementation; không chứa business logic.
9. **API router (`src/presentation/api/v1/<module>.py`):** Dùng `ApiResponseRoute`, khai báo payload `response_model`, `operation_id` ổn định, error responses và type annotation cho path/query/body. Endpoint chỉ map request → input, gọi service interface và trả payload `data`.
10. **Kiểm thử và đồng bộ Frontend:** Viết Domain/Application/API contract tests, chạy Ruff/Pytest, export FastAPI OpenAPI rồi chạy `npm run api:generate`. Frontend chỉ dùng generated types/client; không sửa code trong `src/api/generated/`.

- Khi gọi method ngoài module hiện tại, chỉ phụ thuộc application service interface hoặc Domain repository interface; không import concrete service/repository của module khác.
- Transaction phải đi qua `IUnitOfWork`. Nếu framework chưa có decorator transaction/service chuẩn thì không tự tạo decorator hình thức.

### 0.3. Success response và OpenAPI contract

- Mọi JSON success endpoint phải dùng `ApiResponseRoute`. Endpoint **chỉ trả payload data**; route tự bọc thành `ApiResponse[T]` ở runtime và tự công bố cùng envelope trong OpenAPI.
- Không viết `_success_response()`, không khởi tạo `ApiResponse` trong từng module và không dùng HTTP middleware đọc/ghi lại response body.
- Route phải khai báo `response_model` là payload DTO cụ thể, `operation_id` ổn định và `responses` cho các lỗi đã biết. Không dùng `dict`, `object` hoặc `Any` làm public API response nếu có thể mô hình hóa schema.
- Request/response Pydantic DTO phải có type đầy đủ và metadata `Field` cần thiết. Path/query parameter dùng `Annotated` cùng `Path`, `Query` hoặc `Header` khi cần constraints/description.
- Frontend **MUST NOT** tự định nghĩa lại Backend API Request/Response DTO. API types/client **MUST** sinh từ FastAPI OpenAPI; generated source **MUST NOT** chỉnh sửa thủ công. View model/UI state riêng được phép đặt ngoài thư mục generated và map tường minh với generated types.

### 0.4. Quy tắc đặt tên file, folder và identifier

**Frontend**

- Folder và file kỹ thuật dùng `kebab-case`; React component dùng `PascalCase.tsx`; file do shadcn registry quản lý giữ tên lowercase của registry; test dùng hậu tố `.test.ts` hoặc `.test.tsx`.
- Component, type và interface dùng `PascalCase`; function và variable dùng `camelCase`; hằng số dùng `UPPER_SNAKE_CASE`.
- Boolean bắt đầu bằng `is`, `has`, `should` hoặc `can`; event handler nội bộ dùng `handle*`; callback prop dùng `on*`; hàm API dùng động từ + danh từ.
- Namespace i18n và filename feature dùng `kebab-case`. Translation key phẳng dùng `UPPER_SNAKE_CASE`; không tạo object key lồng nhau.

**Backend**

- Package, module, function và variable dùng `snake_case`; class, exception và DTO dùng `PascalCase`; hằng số và enum value dùng `UPPER_SNAKE_CASE`; private member bắt đầu bằng `_`.
- Interface giữ convention dự án `IName` và file `i_<name>.py`; test đặt theo hành vi với dạng `test_<behavior>.py`.
- Tên phải diễn tả trách nhiệm hoặc nghiệp vụ; không dùng tên mơ hồ như `helper`, `manager`, `data` nếu thiếu ngữ cảnh.

### 0.5. Quy tắc comment và tài liệu API

- Viết tiếng Việt cho exported/public API và logic nội bộ không hiển nhiên. Generated code, migration và component do shadcn registry quản lý được miễn.
- Frontend dùng TSDoc/JSDoc: mô tả mục đích; `@param` cho từng tham số; `@returns` cho giá trị trả về; `@throws` cho lỗi chủ động hoặc được propagate; `@remarks` cho side effect; `@template` cho generic; và `@example` khi cách dùng không rõ. Không thêm tag không áp dụng chỉ để đủ hình thức.
- Backend dùng Google-style docstring với `Args`, `Returns`, `Raises`, `Yields` khi phù hợp. Public method phải nêu business/system exception có thể phát sinh.
- Không comment từng biến hoặc diễn giải lại code hiển nhiên. Comment phải giải thích contract, lý do thiết kế, side effect hoặc ràng buộc khó nhận ra từ code.

### 0.6. Ưu tiên thư viện được duy trì

- Trước khi tự viết parser, serializer, formatter, validator cú pháp, crypto hoặc protocol client, phải đánh giá thư viện chuẩn/được duy trì sẵn có cho cả FE và BE.
- Ưu tiên thư viện có public API rõ ràng, type/type hint, license phù hợp, release còn được duy trì và test corpus tốt. Phiên bản phải được pin bằng lockfile hoặc khoảng version hẹp.
- Bọc dependency bằng adapter/facade nhỏ để model và exception bên thứ ba không leak qua application boundary.
- Chỉ tự triển khai sau khi có ADR ghi rõ vì sao không có thư viện phù hợp, yêu cầu đặc thù và chi phí bảo trì; không copy hoặc fork grammar vào repo khi chưa được duyệt.
- Domain được phép phụ thuộc một parser/validator thuần, deterministic và không I/O khi facade đó hiện thực trực tiếp invariant định dạng. Framework, persistence và network library vẫn bị cấm trong Domain.

---

## I. Yêu Cầu Kỹ Thuật Backend (Python & Clean Architecture)

### 1. Nguyên Tắc Kiến Trúc Clean Architecture
- **Quy tắc phụ thuộc 1 chiều (Dependency Rule):**
  - Các tầng outer như `presentation`, `application`, `infrastructure` được phép gọi vào tầng `domain`.
  - **Tuyệt đối KHÔNG** có chiều ngược lại: Tầng `domain` KHÔNG được import hay phụ thuộc vào bất kỳ tầng nào bên ngoài.
- **Tầng Domain là trung tâm:**
  - Chứa các thực thể (Entities), giá trị (Value Objects) và Interfaces / Abstractions.
  - Không phụ thuộc vào framework (FastAPI), thư viện ngoài (LangChain, SQLAlchemy, Pydantic) hay cơ sở dữ liệu.
- **Tầng Application:**
  - Chứa các kịch bản sử dụng (Use Cases), xử lý luồng nghiệp vụ.
  - Gọi tầng Domain để thực thi các quy tắc nghiệp vụ.
  - Chỉ gọi repository/service interface; không import hoặc gọi trực tiếp concrete Infrastructure implementation.
  - Mỗi module có một interface service, một service implementation và hai package `input/`, `output/`; không tách mỗi method thành một file service.
- **Tầng Infrastructure & Presentation:**
  - `infrastructure`: Hiện thực hóa các interface (kết nối DB, gọi API ngoài, cấu hình LangGraph/LangChain).
  - `presentation`: Tiếp nhận request từ client, điều hướng bằng FastAPI router và trả về kết quả. Tuyệt đối **KHÔNG** viết logic nghiệp vụ trong này.

### 2. Chuẩn Viết Code Python
- **Type Hints bắt buộc 100%:** Tất cả các hàm, tham số và giá trị trả về đều phải có type hint rõ ràng.
- **Giới hạn kích thước:** Tuân thủ duy nhất các giới hạn function/file và quy tắc chọn input model tại Mục 0.1.
- **Docstring chuẩn chỉ:** Tuân thủ quy tắc Google-style tại Mục 0.5.
- **Quy tắc đặt tên (Naming Conventions):**
  - File và Hàm: Dùng `snake_case` (ví dụ: `analyze_query.py`, `def calculate_score()`).
  - Class: Dùng `PascalCase` (ví dụ: `class AgentState:`).
  - Hằng số: Dùng `UPPER_SNAKE_CASE` (ví dụ: `MAX_RETRIES = 3`).
- **Thứ tự Import chuẩn:**
  1. Thư viện tiêu chuẩn Python (`os`, `typing`...).
  2. Thư viện bên thứ ba (`fastapi`, `pydantic`, `langchain`...).
  3. Code nội bộ dự án (`src.domain...`, `src.application...`).

### 3. Quy Định Chuẩn Cho Hệ Thống Xử Lý Lỗi (Exception Handling System)

- **Mô Hình Xử Lý Ngoại Lệ Tập Trung:**
  - Luồng xử lý: `Exception` → `ErrorCode` → `HTTP Status Code` → `Global Exception Handler` → `Standardized Error Response`.
  - **CẤM tạo Exception class riêng cho từng Error Code** (Ví dụ CẤM: `UserNotFoundException`, `RevisionConflictException`...).
  - Các lớp ngoại lệ chính kế thừa từ `AppException`:
    - `BusinessException`: Dùng cho các lỗi nghiệp vụ trong hệ thống (truyền kèm `ErrorCode` phù hợp).
    - `SystemException`: Dùng cho các lỗi kỹ thuật và hệ thống nói chung.
    - `InfrastructureException`: Dùng cho tầng Infrastructure khi catch lỗi từ thư viện/dịch vụ ngoài (kế thừa từ `SystemException`).
  - Mã lỗi (`ErrorCode`) sử dụng `StrEnum` với định dạng `UPPER_SNAKE_CASE` định danh ổn định để Frontend dựa vào `error_code` xử lý logic.

- **Các Nguyên Tắc Xử Lý Ngoại Lệ Cốt Lõi (Exception Handling Principles):**
  1. **Không try/except vô nghĩa hoặc che giấu lỗi:** Không sử dụng `try/except` chỉ để `raise` lại exception nguyên vẹn mà không bổ sung context, hoặc để che giấu/nuốt lỗi.
  2. **Báo lỗi nghiệp vụ bằng `BusinessException` + `ErrorCode`:** Business logic phải báo lỗi bằng `BusinessException(code=ErrorCode..., message=...)`.
  3. **Không tạo exception class riêng cho từng lỗi nghiệp vụ:** CẤM định nghĩa các subclass riêng như `OrderNotFoundException`, `InsufficientBalanceException`.
  4. **Infrastructure Exception Translation:** Tầng Infrastructure có thể catch external/technical exceptions từ thư viện thứ 3 (`SQLAlchemyError`, `OpenAIError`, `RedisError`, `LangGraphError`) để chuyển đổi thành `InfrastructureException` phù hợp.
  5. **Bảo toàn Exception Chain với `raise ... from exc`:** Khi chuyển đổi ngoại lệ, BẮT BUỘC sử dụng cú pháp `raise InfrastructureException(...) from exc` để giữ nguyên gốc vết lỗi (`__cause__`) và stack trace.
  6. **Không chuyển technical/system exception thành business exception vô cơ sở:** Chỉ chuyển đổi ngoại lệ hạ tầng (ví dụ: DB `IntegrityError` do trùng email) thành `BusinessException` khi có căn cứ nghiệp vụ rõ ràng. CẤM tự ý đổi lỗi hệ thống/DB connection thành `BusinessException`.
  7. **Không che giấu exception bằng kết quả mặc định:** Tuyệt đối KHÔNG trả về `None`, kết quả rỗng (empty result) hoặc giá trị mặc định để nuốt/che giấu exception (trừ trường hợp Null-Object Pattern được thiết kế có mục đích rõ ràng).
  8. **Cấm `except Exception` tùy tiện ở Domain/Application/Presentation:** Tránh dùng `except Exception:` broad catch trong các tầng nghiệp vụ, trừ các điểm quan sát cross-cutting (Interceptor, Middleware) hoặc Global Exception Handler.
  9. **Global Exception Handler là boundary cuối cùng:** Global Exception Handler chịu trách nhiệm duy nhất chuyển đổi các exception chưa được bắt thành HTTP response chuẩn hóa.
  10. **Phân tầng trách nhiệm xử lý exception (Layer Context Responsibility):** Exception phải được bắt và xử lý tại tầng có đủ context và thẩm quyền/trách nhiệm xử lý nó.

- **Quy Tắc Phân Tầng Clean Architecture Cho Exception:**
  - **Tầng Domain & Application:** KHÔNG import `fastapi`, `starlette` hay `HTTPException`. Chỉ `raise BusinessException(code=ErrorCode.USER_NOT_FOUND, message="User not found.")`.
  - **Tầng Infrastructure (Infrastructure Exception Translation):** Bắt buộc phải bắt tất cả ngoại lệ từ thư viện thứ 3 (`SQLAlchemyError`, `OpenAIError`, `RedisError`, `LangGraphError`) và chuyển đổi (translate) thành `InfrastructureException(code=ErrorCode.DATABASE_ERROR/LLM_ERROR/...)` với `raise ... from exc` trước khi truyền lên trên. Tuyệt đối không để leak thư viện hạ tầng ra ngoài.
  - **Exception không chứa HTTP Status Code:** Không hard-code HTTP status code trong Exception class. Mọi mapping `ErrorCode → HTTPStatus` được quản lý tập trung duy nhất tại `src/common/exceptions/error_status.py`.

- **Bảo Mật Thông Tin & Logging:**
  - **Bắt ngoại lệ cụ thể (Specific Exception):** CẤM HOÀN TOÀN dùng `except:` rỗng hoặc `except Exception:` mà bỏ qua lỗi (`pass`).
  - **Bảo mật:** Handler toàn cục tự động ẩn toàn bộ thông tin nhạy cảm (stack trace, DB credentials, API keys) ở response trả về client khi xảy ra lỗi 500 (Unhandled Exception).
  - CẤM log dữ liệu nhạy cảm (`password`, `access_token`, `refresh_token`, `api_key`, `secret`).
  - CẤM hard-code số ma (Magic numbers). Phải tạo hằng số `UPPER_SNAKE_CASE`.

- **Tuyệt Đối KHÔNG Dùng Code/Thư Viện Đã Bị Deprecated:**
  - Không sử dụng các cú pháp cũ đã bị cảnh báo ngưng hỗ trợ (ví dụ: cú pháp Pydantic v1 cũ `dict()`, `schema()`, hãy dùng `model_dump()`).
  - Luôn cập nhật và tuân thủ các phương thức mới nhất từ LangChain/LangGraph.

### 4. Quản Lý Cấu Hình & Bảo Mật Secrets
- **CẤM hardcode secrets:** Tuyệt đối không dán API Key, password, token, các trường trong .env trực tiếp vào code. Không fallback gì hết, nếu chạy code không có -> PHẢI báo lỗi.
- **Sử dụng file `.env`:** Quản lý tất cả cấu hình môi trường qua `pydantic-settings` và file `.env`. Đảm bảo file `.env` nằm trong `.gitignore`.

### 5. Kiểm Trả Tự Động (Linting & Testing)
- Tất cả code Python trước khi commit phải vượt qua công cụ kiểm tra syntax và style:
  ```bash
  ruff check src/ tests/
  ```

- Phải có unit test cho mọi hàm xử lý và pass toàn bộ test khi chạy `pytest`.

### 6. Quy Định Thiết Kế DTO (Data Transfer Objects) & Common DTO

- **Phân Định Ranh Giới Common DTO vs Domain DTO:**
  - `src/common/dto/` CHỈ chứa các DTO abstraction **thực sự dùng chung xuyên nhiều module/tầng** (`PaginationRequest`, `PaginationMeta`, `PaginatedResponse`, `SortOrder`, `SortRequest`, `ApiResponse`, `ResponseMeta`).
  - **KHÔNG biến `common/dto/` thành nơi chứa toàn bộ DTO.** Các DTO đặc thù domain/use case (ví dụ: `CreateProjectRequest`, `UpdateRequirementRequest`, `GenerateDataModelRequest`, `ProjectResponse`, `RequirementResponse`...) KHÔNG được đặt trong `common/dto/`, mà phải thuộc module `application` hoặc `presentation` tương ứng.

- **Nguyên Tắc Phụ Thuộc Clean Architecture Cho Common DTO:**
  - `common/dto/` phải là layer cực kỳ nhẹ, CHỈ được phép phụ thuộc vào `pydantic` và thư viện chuẩn của Python.
  - **CẤM HOÀN TOÀN** phụ thuộc hoặc import: `FastAPI`, `SQLAlchemy`, `PostgreSQL`, `Redis`, `Repository`, `Domain Entities`, `Agent`, `LangGraph`, `LLM SDK`, `Langfuse`.

- **Chuẩn Phân Trang (Pagination DTO):**
  - **PaginationRequest:** Sử dụng hằng số chuẩn từ `src.common.constants.pagination` (`DEFAULT_PAGE = 1`, `DEFAULT_PAGE_SIZE = 20`, `MAX_PAGE_SIZE = 100`). Validate `page >= 1` và `1 <= page_size <= MAX_PAGE_SIZE`.
  - **PaginationMeta:** Chứa `page`, `page_size`, `total_items`, `total_pages`. Hỗ trợ factory `PaginationMeta.create(...)` tự động tính `total_pages = ceil(total_items / page_size)`.
  - **PaginatedResponse[T]:** Generic response `data: list[T]`, `meta: PaginationMeta`.
  - **KHÔNG đặt database logic vào DTO:** Common DTO chỉ biểu diễn dữ liệu. KHÔNG import ORM, KHÔNG tạo method `apply(query)` hay tính toán offset DB bên trong DTO.

- **Chuẩn Sắp Xếp (Sorting DTO):**
  - **SortOrder:** StrEnum (`asc`, `desc`).
  - **SortRequest:** `sort_by: str | None = None`, `sort_order: SortOrder = SortOrder.DESC`.
  - Tham số `sort_by` chỉ mang giá trị mô tả request, KHÔNG được tự động đưa trực tiếp vào SQL query. Từng API/usecase chịu trách nhiệm whitelist các field được phép sort.

- **Chuẩn API Success Response Envelope (`ApiResponse[T]`):**
  - Tuân theo cấu trúc phản hồi thành công chuẩn tại Mục III.3: `status` ("success"), `code` (200), `message` ("Xử lý thành công"), `data` (`T | None`).
  - Khi phân trang, bọc `PaginatedResponse[T]` làm payload `data` inside `ApiResponse[PaginatedResponse[T]]`.

- **Pydantic v2 Standard & Type Safety:**
  - 100% sử dụng Pydantic v2 syntax (`ConfigDict`, `Field`, `model_dump()`).
  - Sử dụng Generic Type (`Generic[T]`) rõ ràng, CẤM sử dụng `Any` khi có thể định nghĩa type safety.

### 7. Quy Định Hệ Thống Logging & Tracing (Logging Guidelines)

- **CẤM Dùng `print()` Cho Application Logging:**
  - 100% code backend (Application, Domain, Infrastructure, Presentation, Agent) **tuyệt đối KHÔNG sử dụng `print(...)`**.
  - Tất cả các module phải khởi tạo logger chuẩn hóa:
    ```python
    from src.common.logging import get_logger

    logger = get_logger(__name__)
    ```

- **Quy Tắc Naming Logger:**
  - Luôn sử dụng `__name__` làm name cho logger (ví dụ: `src.application.project.services`, `src.infrastructure.agents.schema_agent`). Cấm hard-code string tên logger tùy tiện.

- **Chuẩn Phân Loại Log Levels:**
  - **DEBUG:** Thông tin chi tiết phục vụ gỡ lỗi (state transition, internal decision...). Không dùng ở Prod mặc định.
  - **INFO:** Các sự kiện quan trọng của hệ thống (`application_started`, `http_request_completed`, `agent_execution_started`, `llm_call_completed`). Không log tràn lan từng dòng code.
  - **WARNING:** Sự cố tự khắc phục được (retry, fallback, slow external API).
  - **ERROR:** Thất bại trong một operation (DB error, LLM call failure, unexpected exception).
  - **EXCEPTION:** Dùng `logger.exception(...)` trong `except` block để lưu đầy đủ traceback. CẤM dùng `logger.error(str(e))` khi cần stack trace.

- **Bảo Mật Thông Tin & Sensitive Data Filtering:**
  - **CẤM HOÀN TOÀN** log các dữ liệu nhạy cảm: `password`, `password_hash`, `access_token`, `refresh_token`, `jwt`, `api_key`, `secret`, `client_secret`, `authorization`.
  - Bộ lọc `SensitiveDataFilter` tự động mask/redact các từ khóa trên thành `"***REDACTED***"`.
  - CẤM log full LLM System/User prompt hoặc full response dài trong application logs. LLM prompt/response tracing phải do hệ thống Observability (như Langfuse) đảm nhiệm.

- **Request Context & Multi-Agent Tracing:**
  - Tự động truyền và ghi nhận `request_id`, `correlation_id`, `session_id`, `agent_name` xuyên suốt luồng xử lý bằng `contextvars` (thread-safe & async-safe).
  - Kết thúc HTTP request, `RequestLoggingMiddleware` tự động dọn dẹp contextvars và trả header `X-Request-ID` cho client.

- **Tách Biệt Logging và Tracing (Langfuse):**
  - **Application Logs (`src/common/logging`):** Dành cho hệ thống vận hành, lỗi, request lifecycle, events.
  - **Agent / LLM Tracing (Langfuse):** Dành cho LLM generation traces, token usage, latency, prompt/response tracing.
  - Kết nối giữa 2 hệ thống thông qua `request_id` và `session_id`. Core logger **KHÔNG import `langfuse`**.

### 8. Quy Định Sử Dụng Common Utilities (`src/common/utils/`)

- **Mục Đích & Nguyên Tắc Đặt Code:**
  - `src/common/utils/` CHỈ chứa các helper hàm thuần kỹ thuật (pure functions), generic, stateless và tái sử dụng cho toàn hệ thống.
  - `utils = generic technical helpers`. CẤM biến `utils` thành nơi chứa tất cả mã nguồn dùng chung hoặc logic nghiệp vụ.
  - **CẤM HOÀN TOÀN** đưa vào `utils`: Business logic, domain rules, truy cập CSDL, gọi API bên ngoài, gọi LLM, gọi Agent, quản lý state application hay phụ thuộc vào FastAPI/SQLAlchemy/Infrastructure.
  - Trước khi tạo utility mới, bắt buộc phải trả lời câu hỏi: *"Function này có thực sự generic và dùng độc lập với business domain hay không?"* Nếu **KHÔNG** -> KHÔNG đặt trong `utils`.

- **Hướng Dẫn Chi Tiết Các Utility Trong System:**

| File Utility | Tên Hàm / Interface | Mô Tả & Tình Huống Sử Dụng |
|---|---|---|
| `datetime.py` | `utc_now() -> datetime` | Lấy thời gian UTC hiện tại có timezone-aware (`timezone.utc`). Dùng cho mọi thao tác ghi nhận thời gian hệ thống. |
| | `ensure_utc(dt: datetime) -> datetime` | Đảm bảo `datetime` object có timezone UTC. Nếu naive sẽ gán UTC, nếu có timezone khác sẽ convert sang UTC. |
| | `to_isoformat(dt: datetime) -> str` | Chuyển đổi `datetime` thành chuỗi định dạng ISO 8601 chuẩn. |
| | `parse_iso_datetime(value: str) -> datetime` | Parse chuỗi ISO 8601 thành `datetime` UTC timezone-aware. Ném `ValueError` nếu sai định dạng. |
| `uuid.py` | `generate_uuid() -> UUID` | Sinh ra `UUID` (version 4) object ngẫu nhiên. Dùng khi domain/entity yêu cầu UUID object. |
| | `generate_uuid_str() -> str` | Sinh ra chuỗi UUIDv4 36 ký tự. Dùng khi cần UUID dạng string (ví dụ: request_id, tracking code). |
| | `is_valid_uuid(val: str \| UUID) -> bool` | Kiểm tra một chuỗi hoặc đối tượng có phải UUIDv4 hợp lệ hay không. |
| `string.py` | `normalize_whitespace(value: str) -> str` | Strip khoảng trắng 2 đầu và gộp nhiều khoảng trắng thừa giữa các từ thành 1 space. |
| | `is_blank(value: str \| None) -> bool` | Kiểm tra chuỗi bị `None`, rỗng `""` hoặc chỉ chứa khoảng trắng. |
| | `truncate(value: str, max_length: int, suffix: str = "...") -> str` | Cắt ngắn chuỗi an toàn theo độ dài tối đa mà không gây rách dữ liệu. |
| | `safe_strip(value: str \| None) -> str \| None` | Strip khoảng trắng nếu là chuỗi, trả về `None` nếu input là `None`. |
| `json.py` | `safe_json_dumps(obj: Any, ...) -> str` | Serialize dữ liệu sang JSON string an toàn, hỗ trợ UUID, datetime, Enum, Decimal, Pydantic BaseModel. Ném `TypeError` rõ ràng nếu gặp type không hợp lệ. |
| | `safe_json_loads(json_str: str) -> Any` | Deserialize chuỗi JSON thành Python object primitives. Ném `ValueError` nếu chuỗi JSON không đúng định dạng. |
| `collections.py` | `chunked(iterable: Iterable[T], size: int) -> list[list[T]]` | Chia một danh sách/iterable thành nhiều sub-list (chunk) có kích thước tối đa `size`. |
| | `is_empty(collection: Collection[Any] \| None) -> bool` | Kiểm tra collection (list, dict, set, tuple) bị `None` hoặc có độ dài 0. |

- **Những Điều CẤM Khi Phát Triển Utilities:**
  - **CẤM** tạo các file mơ hồ như `helpers.py`, `common.py`.
  - **CẤM** đưa I/O utilities (`read_file`, `upload_s3`, `execute_sql`) vào `utils` -> Đặt tại `infrastructure`.
  - **CẤM** đưa Security/Auth utilities (`hash_password`, `generate_jwt`) vào `utils` -> Đặt tại `infrastructure/security`.
  - **CẤM** đưa Logging (`log.py`), Exception (`error.py`), DTO (`pagination.py`) vào `utils` -> Sử dụng các module tương ứng tại `common/logging`, `common/exceptions`, `common/dto`.

### 9. Quy Định Sử Dụng Interceptor Layer (`src/common/interceptors/`)

- **Mục Đích & Ranh Giới Kiến Trúc:**
  - `src/common/interceptors/` cung cấp cơ chế cross-cutting wrapper bao quanh việc thực thi các **Application Operation / Use Case**.
  - **CẤM** nhầm lẫn giữa HTTP Middleware và Application Interceptor:

| Tiêu chí | HTTP Middleware (`common/middleware/`) | Application Interceptor (`common/interceptors/`) |
|---|---|---|
| **Vòng đời (Lifecycle)** | HTTP Request / Response Lifecycle | Application Operation / Use Case Lifecycle |
| **Phụ thuộc HTTP** | Phụ thuộc FastAPI `Request`, `Response`, `Starlette` | **KHÔNG** phụ thuộc FastAPI/HTTP (Headless testable) |
| **Ghi Log (Logging)** | HTTP Request Completion Log (`http_request_completed`) | Application Operation Log (`application_operation_started/completed/failed`) |
| **Đo Thời Gian (Timing)** | Tổng thời gian HTTP Request | Thời gian thực thi Use Case (`duration_ms`) |
| **Ghi nhận Context** | Khởi tạo & nạp `request_id`, `correlation_id` vào ContextVar | Đọc `request_id`, `session_id` từ ContextVar để đính kèm vào Operation Context |
| **Truy Cập CSDL / LLM** | CẤM | CẤM (Interceptor chỉ quan sát, không gọi DB/LLM/Agent) |

- **Nguyên Tắc Phát Triển Interceptors:**
  - **Bảo Toàn Exception:** Interceptor tuyệt đối **KHÔNG được nuốt exception** (`except Exception: pass` hoặc `return None`). Mọi ngoại lệ phải được re-raise để Global Exception Handler xử lý.
  - **Bảo Toàn Return Value:** Interceptor phải trả về chính xác kết quả của Operation mà không tự ý biến đổi hay bọc lại dữ liệu.
  - **Độc Lập Phụ Thuộc:** Interceptor KHÔNG import `fastapi`, `starlette`, `sqlalchemy`, `langgraph`, `langfuse` hay các domain rules.
  - **Bảo Mật Dữ Liệu:** Audit/Logging Interceptor **CẤM** ghi nhận dữ liệu nhạy cảm (`password`, `token`, `api_key`, `secret`, full LLM prompt/response).

---

## II. Yêu Cầu Kỹ Thuật Frontend (Next.js, TypeScript & FSD Architecture)

### 1. Kiến Trúc Thư Mục Feature-Sliced Design (FSD)
Mã nguồn Frontend trong `src/` được chia thành các phân vùng chính:
- `src/app/`: Chỉ dùng cho định tuyến (Routing) theo chuẩn Next.js App Router (`page.tsx`, `layout.tsx`). Khung hiển thị trang gọi đến các module trong `features/`.
- `src/features/`: Chứa toàn bộ logic nghiệp vụ cốt lõi, chia theo từng tính năng độc lập.
- `src/common/`: Chứa các tài nguyên dùng chung cho toàn dự án (UI components như `shadcn/ui`, global hooks, hàm tiện ích utils, global stores).
- `src/api/`: Khởi tạo cấu hình axios/fetch client dùng chung và các kiểu dữ liệu API gốc.

### 2. Nguyên Tắc Đóng Gói (Colocation) & Cấm Gọi Chéo
- **Mỗi Feature là một module độc lập:** Tất cả component, hook, helper chỉ phục vụ cho một tính năng thì phải nằm gọn bên trong thư mục của feature đó (ví dụ: `src/features/hitl-editor/`).
- **CẤM gọi chéo giữa các Feature:** Không được import trực tiếp code từ feature này sang feature khác (ví dụ: `features/A` KHÔNG import từ `features/B`).
- **Tái sử dụng code đúng cách:** Nếu một component hoặc logic cần dùng ở 2 feature trở lên, bắt buộc phải chuyển component/logic đó sang thư mục `src/common/`.

### 3. Quy Ước Code TypeScript & Comment
- **Comment và TSDoc:** Tuân thủ Mục 0.5; ưu tiên tài liệu contract cho public API và không comment code hiển nhiên.
- **Strict TypeScript:** Bắt buộc định nghĩa type/interface rõ ràng cho props và dữ liệu. Không dùng kiểu `any`, `unknown` tùy tiện.

### 4. Framework & Styling
- **Tuân thủ chuẩn Next.js App Router:** Lưu ý các thay đổi breaking changes của Next.js mới. Tránh dùng các hàm hoặc API đã bị cảnh báo deprecated.
- **Styling chuẩn Tailwind CSS:**
  - Sử dụng Tailwind CSS qua class name.
  - Khi cần gộp class động, bắt buộc dùng hàm tiện ích `cn()` (từ `clsx` và `tailwind-merge`).

### 5. Quy Định Chuẩn Cho Đa Ngôn Ngữ & Quản Lý Chuỗi Văn Bản (Frontend i18n Guidelines)
- **CẤM Hardcode Văn Bản Hiển Thị Trong Code UI & Logic:**
  - **NEVER hardcode UI text.** Tuyệt đối không hardcode trực tiếp các chuỗi văn bản (tiếng Việt hay tiếng Anh) trong các file JSX/TSX/TS (`<span>`, `<button>`, `title`, `placeholder`, `aria-label`, alert, toast message, error message...).
  - 100% văn bản hiển thị cho người dùng phải được lấy thông qua `useTranslation()` / `useTranslations()`.
  - **Quy ước đặt tên Translation Keys (Naming Conventions):**
    - `BTN_[ACTION]`: Cho các nút bấm/actions (ví dụ: `BTN_SAVE`, `BTN_CANCEL`, `BTN_SUBMIT`).
    - `TXT_[NAME]`: Cho các tiêu đề, đoạn văn, văn bản chung (ví dụ: `TXT_WELCOME`, `TXT_DESCRIPTION`).
    - `MSG_[TYPE]`: Cho các câu thông báo trạng thái/hệ thống (ví dụ: `MSG_SUCCESS`, `MSG_ERROR_NETWORK`).
    - `[FIELD]_LABEL`: Cho nhãn của các trường input/form (ví dụ: `USERNAME_LABEL`, `PROJECT_NAME_LABEL`).
    - `[FIELD]_PLACEHOLDER`: Cho văn bản placeholder gợi ý nhập (ví dụ: `EMAIL_PLACEHOLDER`, `SEARCH_PLACEHOLDER`).
    - Thêm đầy đủ key còn thiếu vào file JSON tương ứng trong `src/common/i18n/locales/`.

- **Quy Tắc Phân Tầng & Quản Lý Namespace JSON (`src/common/i18n/locales/`):**
  - **Dùng chung (`common.json`):** Chứa các nhãn giao diện, nút bấm, trạng thái, phân trang được sử dụng ở 2 feature trở lên (*Lưu, Hủy, Xóa, Tìm kiếm, Đang tải, Trang...*).
  - **Thông báo (`notifications.json`):** Chứa toàn bộ nội dung tiêu đề và thông điệp Toast/Alert/Modal thông báo tác vụ (*thành công, thất bại, cảnh báo, bắt đầu tác vụ...*).
  - **Mã lỗi Backend (`errors.json`):** Chứa bản dịch tương ứng 1-1 cho tất cả mã lỗi `ErrorCode` được trả về từ Backend API (`INVALID_INPUT_SCHEMA`, `PROJECT_NOT_FOUND`, `UNAUTHORIZED`...).
  - **Theo từng Feature (`{feature-name}.json`):** Mọi văn bản chỉ thuộc về duy nhất một tính năng nghiệp vụ cụ thể bắt buộc phải nằm trong namespace kebab-case tương ứng (ví dụ: `project-init.json`, `hitl-editor.json`, `sandbox-deployment.json`).

- **Quy Định Phát Thông Báo Qua Custom Hook (`useAppNotification`):**
  - **CẤM** hardcode câu chữ khi hiển thị thông báo thành công hoặc báo lỗi trong các hàm xử lý sự kiện hoặc API callbacks (`onSuccess`, `onError`, `catch`).
  - Mọi thông báo thành công hoặc cảnh báo phải được phát thông qua chìa khóa dịch trong `notifications.json`.
  - Mọi thông báo lỗi từ API Backend phải truyền trực tiếp `error_code` nhận từ response vào `useAppNotification` để tự động tra cứu câu chữ tương ứng trong `errors.json`.

- **Strict Type Safety & Đăng Ký Namespace:**
  - Mọi namespace JSON mới khi tạo ra phải được khai báo và import trong `src/common/i18n/i18n.ts` để đảm bảo hỗ trợ autocomplete và type checking qua `i18n.d.ts`.
  - **CẤM** ép kiểu `any` hoặc tắt type check khi gọi chìa khóa i18n trong code.

- **Định Dạng Dữ Liệu Động & Chuyển Đổi Ngôn Ngữ:**
  - Các tham số biến đổi trong câu chữ (ví dụ: số lượng file, tên file, thời gian) bắt buộc phải dùng cú pháp nội hàm `{{paramName}}` của i18next thay vì cộng chuỗi thủ công.
  - Chuyển đổi ngôn ngữ phải thông qua component `LanguageSwitcher` hoặc instance `i18n.changeLanguage()`.

### 6. Quy Ước Đặt Tên Trong React (Naming Conventions)
- **Internal Event Handlers:** `handle[Action][Object]` (ví dụ: `handleSaveQuestion`, `handleCloseModal`, `handleSubmitForm`).
- **Props / Callbacks (nhận từ Component cha):** `on[Action][Object]` (ví dụ: `onSave`, `onClose`, `onSelectProject`).
- **Boolean States:** Bắt đầu bằng `is`, `has`, `should`, `can` (ví dụ: `isLoading`, `hasError`, `shouldShowModal`, `canEdit`).
- **Mutations / API Functions:** Dạng `Verb + Noun` (ví dụ: `createQuestion`, `updateUser`, `deleteProject`).

### 7. Quy Chuẩn UI / UX (UI/UX Rules)
- **Hover Effects:** Bất kỳ phần tử nào có thể click được (*Clickable elements*) **BẮT BUỘC** phải có `cursor: pointer` và hiệu ứng tương tác `hover` rõ ràng.
- **Loading States:**
  - **BẮT BUỘC** sử dụng **Skeleton Loaders** cho trạng thái tải dữ liệu ban đầu (initial data fetching).
  - **TUYỆT ĐỐI KHÔNG** chặn toàn màn hình bằng một spinner khổng lồ (massive spinner).
- **Empty / Error States:** Mọi bảng (table) hoặc danh sách (list) **BẮT BUỘC** phải có:
  - **Empty State:** Hình minh họa (Illustration) + Đoạn văn mô tả (Text hướng dẫn).
  - **Error State:** Thông báo lỗi thân thiện + Nút thử lại (Retry action).
- **Form Validation (Frontend):**
  - Tất cả các form **BẮT BUỘC** phải được validate bằng **Zod schemas** (import từ `api/models/` hoặc thư mục schemas tương ứng).
  - Bắt lỗi validation ngay tại client side và hiển thị thông điệp lỗi trực tiếp ngay bên dưới trường nhập liệu tương ứng.
- **Tái sử dụng Component từ shadcn/ui:** Nếu cần sử dụng các common UI components, hãy cài đặt trực tiếp từ `shadcn/ui` (ví dụ: `button`, `dialog`, `badge`, `textarea`...), **KHÔNG** tạo mới thủ công lặp lại.

---

## III. Quy Chuẩn Giao Tiếp API Frontend - Backend

### 1. Thỏa Thuận Chung
- **Base URL:**
  - Development: `http://localhost:8001/api/v1`
  - Production: `https://<domain>/api/v1`
- **Định dạng dữ liệu:** Hoàn toàn bằng **JSON**.

### 2. Standard HTTP Request Headers
Mọi request gửi từ Frontend lên Backend đều phải đi kèm các Header sau:

| Header | Kiểu dữ liệu | Ví dụ | Mô tả |
|---|---|---|---|
| `Content-Type` | string | `application/json` | Định dạng dữ liệu gửi đi |
| `Accept` | string | `application/json` | Định dạng dữ liệu mong muốn nhận về |
| `Authorization` | string | `Bearer <token>` | Token xác thực JWT (nếu có) |
| `X-Request-ID` | string | `req_9a8b7c6d` | Mã định danh request để truy vết lỗi |
| `X-Client-Version` | string | `1.0.0` | Phiên bản Frontend Client |

### 3. Cấu Trúc Phản Hồi Chuẩn (Standard Response Envelope)
Tất cả các API trả về từ Backend bắt buộc tuân theo khung chuẩn sau:

- **Khi thành công (Status 200 OK):**
  ```json
  {
    "status": "success",
    "code": 200,
    "message": "Xử lý thành công",
    "data": {
      /* Dữ liệu chính trả về */
    }
  }
  ```

- **Khi gặp lỗi (Status 4xx/5xx):**
  ```json
  {
    "code": 400,
    "message": "Mô tả lỗi dễ hiểu cho người dùng",
    "error_code": "INVALID_INPUT_SCHEMA",
    "details": [
      {
        "field": "ten_truong",
        "message": "Chi tiết lý do lỗi"
      }
    ]
  }
  ```
