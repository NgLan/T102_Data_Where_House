# Quy định logic nghiệp vụ hiện hành

## 1. Mục đích và phạm vi

Tài liệu này mô tả các quy tắc nghiệp vụ đang được hệ thống hiện thực. Đây không phải hướng dẫn tổ chức code. Khi tài liệu yêu cầu, database và hành vi API mâu thuẫn nhau, quy tắc nghiệp vụ trong tài liệu này phải được dùng làm căn cứ để thống nhất lại.

Các nguyên tắc chung:

- Mỗi entity có một định danh riêng; hai entity được xem là cùng đối tượng khi cùng ID.
- Mọi đối tượng con phải tham chiếu tường minh tới đối tượng cha; hệ thống không tự tạo ID giả cho Project, User, Requirement, Session hoặc Data Model liên quan.
- Dữ liệu nhập được chuẩn hóa khoảng trắng và enum trước khi lưu.
- Thao tác thay đổi nhiều bản ghi liên quan phải hoàn tất trong cùng một transaction.
- Không tự phát minh state transition, quyền hay cách merge dữ liệu chưa được mô tả.

## 2. User

- Username là bắt buộc, được trim và không vượt quá 100 ký tự.
- Email là bắt buộc, phải đúng cú pháp email và không vượt quá 255 ký tự.
- Email được lưu ở dạng normalized. Việc kiểm tra email không gọi DNS và không xác nhận mailbox có thực sự tồn tại.
- Email sai trả về lỗi nghiệp vụ `INVALID_EMAIL`; username sai dùng nhóm lỗi username.

## 3. Project và Project Member

### 3.1 Thông tin Project

- Project luôn thuộc một User.
- Tên Project được chuẩn hóa khoảng trắng, dài từ 3 đến 255 ký tự.
- Yêu cầu nghiệp vụ thô của Project là tùy chọn khi khởi tạo. Nếu được nhập, nội dung
  được chuẩn hóa khoảng trắng và phải có ít nhất 10 ký tự.
- Domain nghiệp vụ là tùy chọn, được trim và không vượt quá 100 ký tự.
- Description là tùy chọn và được trim.
- Khi tạo Project, hệ thống đồng thời tạo membership `OWNER` cho người tạo trong cùng transaction.

### 3.2 Quyền truy cập

- Chủ sở hữu gốc và thành viên của Project được đọc Project.
- Chỉ membership có role `OWNER` được sửa và xóa Project.
- Người không có membership phù hợp nhận `PERMISSION_DENIED`.

### 3.3 Trạng thái

| Trạng thái hiện tại | Trạng thái được chuyển tới |
| ------------------- | -------------------------- |
| `ACTIVE`            | `ANALYZING`, `ARCHIVED`    |
| `ANALYZING`         | `ACTIVE`                   |
| `ARCHIVED`          | `ACTIVE`                   |

- Chỉ Project `ACTIVE` được sửa thông tin.
- Không cho phép tự chuyển về cùng trạng thái hoặc chuyển ngoài bảng trên.

## 4. Requirement

- Requirement luôn thuộc một Project tồn tại.
- Type hợp lệ: `BUSINESS`, `ANALYTICAL`, `TECHNICAL`.
- Priority hợp lệ: `HIGH`, `MEDIUM`, `LOW`; mặc định là `MEDIUM`.
- Title là bắt buộc, được trim và không vượt quá 255 ký tự.
- Description là bắt buộc và được trim.
- Danh sách Requirement được lấy theo Project; Project không tồn tại phải trả `PROJECT_NOT_FOUND`.
- Màn hình Project Init chia vùng yêu cầu thành hai phần: bên trái là yêu cầu nghiệp vụ thô của Project; bên phải là bảng Requirement đã được chuẩn hóa/phân loại. Mũi tên trái sang phải thể hiện luồng phân tích từ yêu cầu thô sang Requirement có cấu trúc.
- Bảng bên phải hiển thị ba cột `requirement`, `type`, `priority`, cho phép OWNER chỉnh sửa dữ liệu và cho phép mọi thành viên có quyền đọc sắp xếp bằng cách nhấn tiêu đề cột `type` hoặc `priority`. Mỗi lần nhấn đảo chiều tăng/giảm.
- Nhãn, enum và trạng thái rỗng của bảng phải hỗ trợ đầy đủ tiếng Việt và tiếng Anh.
- Trong mô hình dữ liệu hiện tại, các hàng của bảng này là entity `Requirement` vì `type` và `priority` thuộc entity đó. `AnalyticalRequirement` là kết quả phân tích sâu hơn (metric, dimension, grain, aggregation) và không được đánh tráo hai khái niệm.
- **Bóc tách tài liệu yêu cầu (DOCX / TXT / MD):** Được xử lý trực tiếp tại phía Client (UI). Trình duyệt đọc và trích xuất nội dung văn bản từ tệp, sau đó tự động điền vào ô nhập yêu cầu nghiệp vụ trên giao diện để người dùng xem/chỉnh sửa trước khi lưu. Backend chỉ tiếp nhận yêu cầu nghiệp vụ dưới dạng chuỗi văn bản (`requirement: str`).

## 5. Analytical Requirement

- Analytical Requirement phải tham chiếu tới một Requirement qua `requirement_id`.
- Phương thức tổng hợp, nếu có, chỉ nhận `SUM`, `AVG`, `COUNT`, `COUNT_DISTINCT`, `MAX` hoặc `MIN`.
- Metric, dimension, time granularity và grain hiện là dữ liệu tùy chọn.
- Hiện chưa có use case CRUD riêng cho Analytical Requirement; các bản ghi chủ yếu được sinh và lưu trong pipeline phân tích Data Model.
- Analytical derivation chỉ dùng Requirement đã rõ semantic; không dùng source availability để thay đổi, làm yếu hoặc bỏ Requirement.
- Mỗi Analytical Requirement persist Source Coverage assessments theo required business concept. Trạng thái hợp lệ là `SUPPORTED`, `NEEDS_SOURCE_CONFIRMATION`, `MISSING_SOURCE`.
- `NEEDS_SOURCE_CONFIRMATION` bắt buộc có candidate exact reference; `MISSING_SOURCE` không được có candidate hoặc tên cột giả định.

## 6. Data Source

### 6.1 Quyền và upload

- Thành viên Project được xem danh sách và preview nguồn dữ liệu.
- Chỉ `OWNER` được upload, sửa metadata cột hoặc xóa nguồn dữ liệu.
- Được upload tối đa 20 file; mỗi file tối đa 20 MB.
- Luồng upload Data Source trên Backend chỉ tiếp nhận và xử lý CSV để trích xuất schema metadata và lưu trữ. Frontend đọc DOCX bằng Mammoth, đọc TXT/MD bằng `File.text()`, điền raw Requirement rồi lưu qua Project API; các tài liệu này không được gửi tới Data Source API.
- Upload lại CSV trùng tên, không phân biệt hoa thường, thay file và schema snapshot của Data Source hiện có.

### 6.2 Data Source và schema metadata

- Data Source phải có Project, name và location; name/location được trim và không rỗng.
- Name không vượt quá 255 ký tự.
- Các loại Data Source được nhận diện: `CSV`, `EXCEL`, `JSON`, `SQL`, `TEXT`. Danh sách này không có nghĩa mọi loại đều được endpoint upload hiện tại hỗ trợ.
- Metadata schema là snapshot bất biến gồm table, column và relationship.
- Table metadata persist `row_count`. Column/relationship có thể chứa USER semantic annotation typed gồm `business_concept`, `CONFIRMED | REJECTED` và provenance `USER`; profiler không được tạo annotation này.
- `data_type` chỉ nhận `TEXT`, `CATEGORY`, `INTEGER`, `NUMBER`, `DECIMAL`, `DATE`, `TIME`, `DATETIME` hoặc `BOOLEAN`; `CATEGORY` là một giá trị trực tiếp, không có lớp semantic type riêng.
- CSV profiler gán `CATEGORY` khi cột phù hợp và chỉ thu thập `distinct_values` cần thiết; không lưu sample/options legacy.
- Constraint là discriminated union: `FOREIGN_KEY(type, reference_table, reference_column)`, `UNIQUE(type)`, `CHECK(type, expression)` hoặc `DEFAULT(type, value)` với value là string, number, boolean hoặc null. `primary_key` và `nullable` vẫn là field riêng.
- Không suy observed statistics thành business/database constraint.
- Uniqueness, distinct count, key candidate và name similarity không tự chứng minh business identity.
- Upload thay thế source xóa semantic annotations của chính source đó; mutation source khác không xóa confirmation còn hợp lệ.
- PATCH column là partial update của `data_type`, `distinct_values`, `constraints` và bắt buộc có ít nhất một field.
- Không tìm thấy table/column cần sửa trả `DATA_SOURCE_COLUMN_NOT_FOUND` và không thay snapshot hiện tại.

## 7. Project Session và Session Event

### 7.1 Project Session

- Session luôn thuộc một Project và một User.
- Title rỗng được chuẩn hóa thành `Untitled Session`.
- Status hợp lệ: `ACTIVE`, `COMPLETED`, `ARCHIVED`.
- Hiện hệ thống mới kiểm tra giá trị status, chưa áp dụng state machine chuyển trạng thái cho Session. Không suy diễn thêm transition chỉ từ tên enum.

### 7.2 Ma trận Session Event

| Event type     | Role được phép  | Content        | Metadata                        |
| -------------- | --------------- | -------------- | ------------------------------- |
| `MESSAGE`      | `USER`, `AGENT` | Bắt buộc       | `MessageMetadata` hoặc không có |
| `QUESTION`     | `AGENT`         | Bắt buộc       | Không có                        |
| `ANSWER`       | `USER`          | Bắt buộc       | Không có                        |
| `AGENT_CALL`   | `AGENT`         | Không bắt buộc | Bắt buộc `AgentCallMetadata`    |
| `AGENT_RESULT` | `AGENT`         | Không bắt buộc | Bắt buộc `AgentResultMetadata`  |
| `TOOL_CALL`    | `AGENT`         | Không bắt buộc | Bắt buộc `ToolCallMetadata`     |
| `TOOL_RESULT`  | `TOOL`          | Không bắt buộc | Bắt buộc `ToolResultMetadata`   |

- Event phải có `session_id`; thiếu tham chiếu trả `INVALID_SESSION_EVENT_REF`.
- Role/type sai, content bắt buộc bị rỗng, hoặc metadata sai loại trả `VALIDATION_ERROR`.
- Kết quả Agent `CANCELLED` không có error được gán thông báo hủy mặc định.

## 8. Data Model

### 8.1 Snapshot DBML

- Mỗi Project có tối đa một Data Model hiện hành.
- DBML được lưu nguyên chuỗi text; revision bắt đầu từ 1 và luôn là số nguyên dương.
- Domain chỉ bảo vệ invariant chuỗi không rỗng; Application bắt buộc gọi Validation Engine trước create, proposal và Accept.
- Parse lỗi được chuẩn hóa thành `INVALID_DBML_CONTENT`.
- Validation Engine kiểm tra parse, bảng/cột/reference tồn tại, trùng bảng/cột/relationship và PK/grain tối thiểu.
- Chỉ issue mức `ERROR` chặn persistence hoặc kích hoạt design retry; `WARNING` được trả để hiển thị.

### 8.2 Khởi tạo, proposal và revision conflict

- Chỉ initial `Save & Analyze` được tạo Data Model đầu tiên ở revision 1.
- Chỉnh sửa DBML thủ công trong editor cập nhật trực tiếp `data_models` bằng optimistic `base_revision` và tăng revision đúng 1.
- `generate` chỉ tạo model đầu tiên và conflict nếu model đã tồn tại. `regenerate` dùng DWDesignAgent từ Requirements, Analytical Requirements và SchemaMetadata, validate rồi ghi đè trực tiếp bằng optimistic locking và tăng revision; không tạo proposal.
- Chỉ AI edit từ instruction của User tạo `DataModelChange(PROPOSED)` và chờ Human Review.
- Proposal chỉ giữ `base_revision` của Data Model tại thời điểm tạo.
- Accept thay DBML và tăng revision đúng 1 khi `base_revision` còn khớp revision hiện tại.
- Base revision cũ làm proposal `is_outdated`; Accept chuyển proposal sang `CONFLICTED` và trả `PROPOSAL_OUTDATED`.

### 8.3 Human Review dành cho thay đổi do AI

- AI edit từ instruction tạo bản ghi Human Review; Update Data Model từ input mới dùng `regenerate` và ghi đè trực tiếp sau validation.
- Lưu DBML thủ công không tạo proposal; snapshot được cập nhật ngay khi optimistic revision còn khớp.
- Proposal có `base_revision`, actor, `proposed_dbml` và trạng thái ban đầu `PROPOSED`.
- Actor lấy từ Application access policy; Infrastructure Agent không biết user hay HTTP request.

### 8.4 Một proposal đang chờ cho mỗi người dùng

- Tại mọi thời điểm, mỗi cặp `(data_model_id, user_id)` chỉ có tối đa một bản ghi trạng thái `PROPOSED`.
- Khi đã có proposal đang chờ, request tạo tiếp sẽ thay thế proposal cũ (Không Accept hay Reject mà là thay trường proposed_dbml thành giá trị mới).
- Nếu người dùng không xử lý proposal -> Mặc định sẽ giữ bản dbml cũ.
- Proposal conflict chỉ khi Data Model revision khác `base_revision` của proposal.
- Analyzed revisions thay đổi không làm proposal conflict; chúng chỉ làm Data Model `is_outdated` khi lệch generated revisions.
- Hai người dùng khác nhau có thể mỗi người có một proposal đang chờ trên cùng Data Model.

### 8.5 Review proposal và conflict

| Trạng thái hiện tại | Trạng thái kết thúc hợp lệ           |
| ------------------- | ------------------------------------ |
| `PROPOSED`          | `ACCEPTED`, `REJECTED`, `CONFLICTED` |
| `ACCEPTED`          | Không có                             |
| `REJECTED`          | Không có                             |
| `CONFLICTED`        | Không có                             |

- Accept chỉ áp dụng khi proposal còn `PROPOSED` và `base_revision` còn khớp revision Data Model hiện tại. DBML đề xuất thay snapshot, revision tăng 1 và proposal thành `ACCEPTED`.
- Nếu revision không khớp, proposal thành `CONFLICTED`, trạng thái này được lưu; DBML và revision hiện tại tuyệt đối không đổi. Hệ thống không tự merge.
- Reject chỉ chuyển proposal từ `PROPOSED` sang `REJECTED`; DBML và revision hiện tại không đổi.
- Proposal đã kết thúc không được Accept, Reject hoặc xử lý lần hai.

## 9. Sandbox

- DDL là output của Data Model và được sinh qua Data Model service. Sandbox chỉ quản lý config, kiểm tra kết nối và thực thi DDL đã nhận.
- Mỗi Project có tối đa một cấu hình Sandbox.
- Hiện chỉ hỗ trợ PostgreSQL; các enum database khác chưa được phép cấu hình.
- Host và database name là bắt buộc; port nằm trong khoảng 1–65535.
- Schema là tùy chọn nhưng, nếu có, phải là SQL identifier bắt đầu bằng chữ hoặc dấu gạch dưới và chỉ gồm chữ, số, dấu gạch dưới.
- Khi cập nhật mà password mới để trống, hệ thống giữ password hiện có.
- GET cấu hình không tự tạo cấu hình mặc định.
- Không được thực thi DDL khi Project chưa có cấu hình Sandbox; trả `SANDBOX_CONFIG_NOT_FOUND`.
- Kết quả thực thi ghi nhận số statement thành công/thất bại và log từng statement.

## 10. Các miền chưa có quy tắc hoàn chỉnh

- `AuthService`, `AnalyticalRequirementService` và `SessionService` hiện chưa có use case nghiệp vụ đầy đủ ngoài contract/khung service.
- Không xem tên class, enum hoặc nội dung REQUIREMENTS tương lai là hành vi đã hiện thực. Khi bổ sung nghiệp vụ, phải cập nhật tài liệu này cùng test và ràng buộc database liên quan.

## 11. Che thông tin cá nhân trước khi gọi LLM

- Văn bản tự do phải được phân tích và anonymize bằng Microsoft Presidio trước khi gửi tới LLM khi `PII_MASKING_ENABLED=true`.
- Mỗi lần detect/mask nhận một language code đã cấu hình. Khi caller không truyền language, hệ thống dùng `PII_DEFAULT_LANGUAGE`; language ngoài `PII_SUPPORTED_LANGUAGES` là lỗi cấu hình hạ tầng, không tự suy đoán ngôn ngữ.
- Entity chỉ được che khi có trong masking policy của lần gọi. Policy mặc định thay:
  `EMAIL_ADDRESS → <EMAIL>`, `PHONE_NUMBER → <PHONE>`,
  `CREDIT_CARD → <PAYMENT_CARD>`, `PERSON → <PERSON>`,
  `LOCATION → <LOCATION>` và `VN_CCCD`/`VN_CMND → <ID_NUMBER>`.
- Email, số điện thoại và thẻ thanh toán ưu tiên built-in recognizer có validation của Presidio. Rule CCCD/CMND, PERSON và LOCATION tiếng Việt là recognizer plugin riêng; core masking service không chứa regex hoặc nhánh xử lý theo ngôn ngữ.
- CCCD/CMND và named entity rule-based chỉ đạt ngưỡng che khi có context phù hợp và vượt validation tối thiểu. Chuỗi số đơn thuần có confidence thấp phải giữ nguyên để giảm false positive.
- Recognizer mới được đăng ký qua registry. Thêm loại PII/ngôn ngữ mới chỉ bổ sung provider, recognizer và policy tương ứng; không sửa orchestration detect → anonymize.
- NLP engine mặc định không tải model NER. Composition root có thể truyền Presidio `NlpEngine` khác để tích hợp Vietnamese NER, spaCy, Stanza hoặc Transformers mà không thay đổi public masking contract.
- Analyzer engine, anonymizer engine và recognizer registry được tái sử dụng giữa các request; không khởi tạo lại model hoặc registry cho từng lần mask.
- Che tên cột nhạy cảm trong DBML là cơ chế placeholder có hoàn nguyên riêng. Mapping chỉ sống trong một lần gọi LLM và hệ thống fail closed nếu placeholder bị biến dạng.

## 12. Agent Workflow và freshness

### 12.1 Operation độc lập

- RequirementAgent có ba operation: clarification/structure Requirements, derive AnalyticalRequirements không dùng source, và evaluate Source Coverage với SchemaMetadata.
- DWDesignAgent có operation initial design và revision. Mỗi lần gọi operation thực hiện đúng một `ainvoke()`; không ReAct, planner, tool loop, graph hoặc SDK retry.
- Profile trong `SchemaMetadata` chỉ do parser/profiler tạo. Semantic confirmation chỉ do OWNER action ghi; LLM không được ghi annotation.
- Analytical output bắt buộc mang `source_requirement_id` tồn tại; không được gắn fallback vào requirement đầu tiên.
- Application có thể gọi tối đa ba DWDesign operation độc lập khi Validation Engine trả issue mức `ERROR`. Attempt sau nhận DBML vừa validation thất bại và danh sách issue.

### 12.2 Save & Analyze và Analyze Changes

- `GET analysis-status` chỉ đọc trạng thái, không gọi Agent. `reanalyze` chỉ cập nhật kết quả phân tích cần thiết và không sửa Data Model.
- Project chưa có model: workflow chạy clarification, analytical derivation, Source Coverage và readiness gate; chỉ `READY_FOR_DESIGN` mới gọi initial DW design.
- Project đã có model: `regenerate` chạy DWDesignAgent từ input/analysis hiện tại, validate rồi ghi đè snapshot bằng optimistic locking và tăng revision.
- Raw Requirement đổi thì chạy lại clarification, derivation và coverage. Chỉ Data Source hoặc semantic annotation đổi thì chỉ chạy coverage. Input revisions không đổi thì không gọi LLM.
- Coverage blocker là normal persisted state, không phải generic error detail. Readiness dùng `REQUIREMENT_CLARIFICATION_REQUIRED`, `SOURCE_CONFIRMATION_REQUIRED`, `SOURCE_DATA_REQUIRED`, `READY_FOR_DESIGN`.
- `GET /source-coverage` reload stable batch. OWNER resolution xác minh batch/source/item revision và chỉ persist đúng item, không gọi Agent. Recheck chỉ hợp lệ khi không còn item `PENDING`; nó materialize scoped USER annotations, tăng source revision đúng một lần cho cả batch rồi chỉ rerun Source Coverage.
- Confirmation item có trạng thái `PENDING`, `CONFIRMED`, `REJECTED`; confirm/reject item này không thay đổi, disable hoặc xóa item khác. Batch và resolved progress phải sống qua reload.
- Database transaction không được mở trong thời gian gọi LLM. Trước persistence phải kiểm tra lại revision; input đổi đồng thời trả `ANALYSIS_INPUT_CHANGED`.

### 12.3 Revision và trạng thái outdated

- Project giữ revision riêng cho Requirement, analytical derivation, source và coverage (`covered_analytical_requirement_revision`).
- Save Raw Requirement hoặc Requirement có cấu trúc thực sự thay đổi tăng requirement revision. Raw Requirement vẫn là nguồn của operation cấu trúc hóa. Upload, thay thế, sửa metadata hoặc xóa source tăng source revision.
- Analytical derivation chỉ outdated khi Requirement đổi. Coverage outdated khi Requirement/Analytical Requirement hoặc source revision đổi; assessment blocked nhưng đã persist là current, không phải outdated.
- Data Model giữ hai generated revisions và là outdated khi chúng lệch analyzed revisions hiện tại.
- Proposal giữ model base revision; chỉ khi revision này lệch snapshot hiện hành proposal mới `CONFLICTED`.
- Source mutation chỉ parser/profile rồi tăng revision; không tự gọi Agent.

### 12.4 Độc lập nhà cung cấp LLM

- Application chỉ phụ thuộc Agent ports; provider SDK chỉ nằm tại Infrastructure.
- Registry mặc định hỗ trợ `openai`, `openai_compatible` và `google`; provider mới chỉ cần đăng ký builder trả `BaseChatModel`.
- Model được khởi tạo lazy và cache theo process. Endpoint không dùng AI vẫn hoạt động khi chưa cấu hình API key.
