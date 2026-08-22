# Tài liệu Mô tả Kiến trúc System & Luồng Dữ liệu (Data Flow Diagram)

## 1. Tổng quan Hệ thống

Hệ thống là một quy trình tự động hóa thiết kế Kho dữ liệu (Data Warehouse Design) sử dụng các **LLM Agent** kết hợp với kiểm duyệt an toàn dữ liệu (**PII Guard**), kiểm tra lỗi tự động (**Validation Engine**), kiểm thử tự động trên môi trường giả lập (**Sandbox**) và sự can thiệp/phê duyệt của con người (**Human Review**).

---

## 2. Các Thành phần chính trong Hệ thống

### 2.1. Giao diện & Người dùng (Frontend & User)

- **User**: Người dùng cuối gửi yêu cầu, prompt điều chỉnh, tải file SQL và nhận kết quả sinh mã cuối cùng.
- **Chỗ nhập dữ liệu đầu vào (Input Data Form)**: Tiếp nhận `Requirement/Source Data` từ User.
- **Chỗ nhập prompt (Prompt Form)**: Tiếp nhận `Prompt` chỉ thị từ User.
- **Chức năng Tải File SQL**: Cho phép người dùng xuất và tải file SQL (DDL/DML) trực tiếp từ mã DBML.

### 2.2. Xử lý Backend & Lưu trữ (Backend & PostgreSQL)

- **Backend**: Tiếp nhận dữ liệu từ Frontend, persist input và điều phối các Agent operation tại Application layer.
- **PostgreSQL**: Cơ sở dữ liệu trung tâm lưu trữ:
  - Raw Requirements (Yêu cầu thô)
  - Source Data (Dữ liệu nguồn thô)
  - `data_models`: Lưu trữ mã DBML chính thức/hiện tại của hệ thống.
  - `data_model_changes`: Lưu trữ lịch sử đề xuất thay đổi mô hình dữ liệu (trạng thái `PROPOSED`, `base_revision=N`).

## 2.3. Hệ thống Agent AI

Hệ thống sử dụng các Agent chuyên trách kết hợp với các thành phần xử lý deterministic.

### Application workflow

Application workflow chịu trách nhiệm điều phối các bước xử lý của hệ thống.

Application workflow không tự phân tích hoặc thiết kế, mà:

- xác định workflow cần thực hiện dựa trên hành động của User hoặc prompt được gửi vào;
- gọi Agent phù hợp;
- truyền đúng input và kết quả cần thiết giữa các bước;
- quản lý trạng thái workflow;
- xử lý retry khi Validation Engine trả về lỗi;
- dừng workflow và trả lỗi nếu vượt quá số lần retry cho phép.

Đối với các hành động rõ ràng trên giao diện như:

- `Save & Analyze`;
- `Analyze Changes`;
- `Update Data Model`;
- chỉnh sửa Data Model bằng AI;

workflow được xác định trực tiếp từ hành động của User, không cần sử dụng LLM để tự suy đoán intent.

Intent classifier cho Agent Chat là capability tương lai; các action hiện tại route trực tiếp tới use case xác định.

---

### RequirementAgent

RequirementAgent chịu trách nhiệm toàn bộ quá trình phân tích Requirement và có hai nhiệm vụ chính.

#### 1. Phân tích Raw Requirement

Input:

```text
projects.requirement
```

Output:

```text
requirements
```

RequirementAgent chuyển Raw Requirement do User nhập thành các Requirement có cấu trúc và rõ nghĩa hơn, bao gồm:

- `BUSINESS`;
- `ANALYTICAL`;
- `TECHNICAL`.

Ví dụ:

```text
Raw Requirement:

"Tôi muốn theo dõi doanh thu bệnh viện,
số lượt khám theo khoa và theo tháng."

        ↓

Requirements:

BUSINESS
- Theo dõi hiệu quả hoạt động bệnh viện.

ANALYTICAL
- Phân tích doanh thu theo khoa và thời gian.
- Phân tích số lượt khám theo khoa và thời gian.
```

Các Requirement sau khi được phân tích được lưu vào bảng `requirements`.

#### 2. Phân tích Analytical Requirement

Sau khi có:

```text
Requirements
+
SchemaMetadata
```

RequirementAgent tiếp tục phân tích để tạo:

```text
AnalyticalRequirements
```

bao gồm các thông tin như:

- Metric;
- Dimension;
- Time Granularity;
- Aggregation Method;
- Grain.

Ví dụ:

```text
Requirement:
"Phân tích doanh thu theo khoa theo tháng"

+
SchemaMetadata

        ↓ RequirementAgent

Metric:
Revenue

Dimension:
Department

Time Granularity:
MONTH

Aggregation:
SUM

Grain:
Revenue transaction
```

Kết quả được lưu vào bảng `analytical_requirements`.

Hai bước trên thuộc cùng trách nhiệm phân tích Requirement nên sử dụng cùng `RequirementAgent`, nhưng có thể được triển khai thành các node/operation riêng trong workflow.

---

### DWDesignAgent

DWDesignAgent chịu trách nhiệm thiết kế và điều chỉnh Data Warehouse Model.

Agent hỗ trợ hai trường hợp.

#### Sinh Data Model

Input:

```text
Requirements
+
AnalyticalRequirements
+
SchemaMetadata
```

Output:

```text
DBML
```

Agent thiết kế Data Warehouse bao gồm:

- Fact Table;
- Dimension Table;
- Grain;
- Measure;
- Column;
- Data Type;
- Primary Key;
- Foreign Key;
- Unique Constraint;
- Nullability;
- Relationship;
- các ràng buộc cần thiết;
- Table Group nếu thiết kế yêu cầu;
- các thành phần DBML khác cần thiết.

#### Chỉnh sửa Data Model bằng AI

Input:

```text
Current DBML
+
User Prompt
+
Requirements
+
AnalyticalRequirements
+
SchemaMetadata
```

Output:

```text
Proposed DBML
```

DWDesignAgent sử dụng Data Model hiện tại làm cơ sở và chỉnh sửa theo yêu cầu của User.

Agent không trực tiếp ghi đè Data Model hiện tại trong workflow yêu cầu Human Review.

---

## 2.4. Phân tích Source Data

Source Data trong MVP chủ yếu là CSV.

Việc đọc và phân tích các thông tin có thể xác định một cách deterministic **không sử dụng LLM Agent**.

Luồng:

```text
CSV
 ↓
CSV Parser / Data Profiler
 ↓
SchemaMetadata
```

Parser / Profiler chịu trách nhiệm xác định các thông tin có thể suy ra trực tiếp từ dữ liệu, ví dụ:

```text
column name
data type
nullable
row count
null count
distinct count
distinct ratio
min / max
distinct values cần thiết cho CATEGORY
uniqueness
data statistics
```

Ví dụ:

```text
patient_id
type = INTEGER
nullable = false
distinct_ratio = 1.0

gender
data_type = CATEGORY
distinct_values = ["Nam", "Nữ", "Khác"]

birth_date
type = DATE
min_value = 1945-01-01
max_value = 2025-01-01
```

Các giá trị như `min_value` hoặc `max_value` được lấy từ dữ liệu hiện có chỉ là **observed statistics**, không tự động được xem là business constraint.

Ví dụ:

```text
observed_min(age) = 18
observed_max(age) = 92
```

không đồng nghĩa với:

```text
CHECK age BETWEEN 18 AND 92
```

Nếu source cung cấp constraint chính thức như PK, FK, UNIQUE, NOT NULL hoặc CHECK thì hệ thống có thể extract chúng trực tiếp.

Column contract dùng `data_type` enum gồm `TEXT`, `CATEGORY`, `INTEGER`, `NUMBER`, `DECIMAL`, `DATE`, `TIME`, `DATETIME`, `BOOLEAN`. Constraint là discriminated union `FOREIGN_KEY`, `UNIQUE`, `CHECK`, `DEFAULT`; `primary_key` và `nullable` là field riêng. Profiler không suy observed statistics thành constraint.

Kết quả phân tích được lưu vào:

```text
data_sources.schema_metadata
```

Không sử dụng `SourceDataAgent` để phân tích lại SchemaMetadata đã được parser/profiler xác định.

---

## 2.5. Validation Engine

Validation Engine là thành phần deterministic/code-based chịu trách nhiệm kiểm tra DBML được DWDesignAgent tạo ra.

Validation bao gồm ít nhất hai nhóm.

### DBML / Technical Validation

Ví dụ:

- cú pháp DBML;
- Table/Column tồn tại;
- PK/FK hợp lệ;
- reference hợp lệ;
- duplicate relationship;
- invalid relationship;
- các structural constraint khác.

### Data Warehouse Design Validation

Validation Engine kiểm tra Data Model theo các Data Warehouse Design Rules đã được hệ thống quy định.

Có thể bao gồm:

- Fact Table phải có Grain rõ ràng;
- Measure phải phù hợp với Grain;
- Fact–Dimension Relationship hợp lệ;
- Dimension Key phù hợp;
- tránh Fan Trap;
- tránh Chasm Trap;
- kiểm tra các rule theo Kimball hoặc rule đã được project quy định;
- Requirement / Analytical Requirement quan trọng phải được phản ánh trong Data Model;
- mapping tới Source Data phải có căn cứ khi workflow yêu cầu.

Nếu Validation thất bại:

```text
Validation Error
      ↓
Application workflow
      ↓
DWDesignAgent
      ↓
DBML mới
```

Hệ thống retry tối đa **3 lần**.

Nếu sau 3 lần DBML vẫn không đạt validation:

```text
Workflow FAILED
```

và Backend trả lỗi phù hợp cho User.

---

# 3. Chi tiết Luồng Dữ liệu

## Bước 1 — User tạo Project và bắt đầu phân tích

User nhập:

```text
Raw Requirement
+
Source Data
```

tại màn hình Project Init.

Nếu User chọn tài liệu Requirement, Frontend đọc DOCX bằng Mammoth `extractRawText({ arrayBuffer })` hoặc đọc TXT/MD bằng `File.text()`, sau đó điền raw text vào Requirement editor. Backend không có API upload Requirement document. Chỉ CSV được gửi tới Data Source upload API.

Khi User chọn:

```text
Save & Analyze
```

Frontend gửi dữ liệu tới Backend.

Backend thực hiện:

```text
Raw Requirement
      ↓
projects.requirement

Source Data
      ↓
File Storage
+
data_sources
```

Đối với CSV, Backend ngay lập tức thực hiện:

```text
CSV
 ↓
Parser / Profiler
 ↓
SchemaMetadata
 ↓
data_sources.schema_metadata
```

Đây là bước deterministic và không cần Agent.

Sau khi dữ liệu đầu vào đã được lưu và SchemaMetadata đã sẵn sàng, Backend kích hoạt Agent workflow.

---

## Bước 2 — Requirement Analysis

`GET /projects/{project_id}/analysis-status` chỉ đọc các cờ outdated và không gọi Agent. Khi User chọn Analyze Changes, `POST /projects/{project_id}/reanalyze` mới gọi `RequirementAgent`; luồng này không sửa Data Model.

### Bước 2.1 — Raw Requirement → Requirements

```text
projects.requirement
      ↓
RequirementAgent
      ↓
Requirements
      ↓
PostgreSQL.requirements
```

RequirementAgent phân tích Raw Requirement thành các Requirement:

```text
BUSINESS
ANALYTICAL
TECHNICAL
```

---

### Bước 2.2 — Requirements + SchemaMetadata → AnalyticalRequirements

Sau khi có:

```text
Requirements
+
SchemaMetadata
```

Application workflow tiếp tục gọi `RequirementAgent` với operation phân tích Analytical Requirement.

```text
Requirements
+
SchemaMetadata
      ↓
RequirementAgent
      ↓
AnalyticalRequirements
      ↓
PostgreSQL.analytical_requirements
```

Analytical Requirement có thể bao gồm:

```text
Metric
Dimension
Time Granularity
Aggregation Method
Grain
```

---

## Bước 3 — Sinh Data Warehouse Model

Sau khi có đầy đủ:

```text
Requirements
+
AnalyticalRequirements
+
SchemaMetadata
```

Application workflow gọi:

```text
DWDesignAgent
```

`POST /projects/{project_id}/data-model/generate` chỉ dùng khi Project chưa có Data Model và conflict nếu snapshot đã tồn tại. Khi model đã tồn tại, `POST /projects/{project_id}/data-model/regenerate` chạy cùng input thiết kế, validate, kiểm tra lại input revisions và model revision rồi ghi đè atomically, tăng revision đúng 1 và không tạo proposal.

Luồng:

```text
Requirements
+
AnalyticalRequirements
+
SchemaMetadata
      ↓
PII Guard
      ↓
DWDesignAgent
      ↓
PII Guard
      ↓
DBML
```

PII Guard bảo đảm dữ liệu nhạy cảm được xử lý phù hợp trước khi gửi tới LLM API.

DWDesignAgent sinh Data Warehouse Model dưới dạng DBML.

---

## Bước 4 — Validate Data Model

DBML được gửi vào:

```text
ValidationEngine
```

Luồng:

```text
DWDesignAgent
      ↓
DBML
      ↓
ValidationEngine
```

### Nếu PASS

```text
Validation PASS
      ↓
Data Model hợp lệ
```

Đối với lần sinh Data Model đầu tiên, DBML hợp lệ có thể được lưu làm Data Model ban đầu theo workflow được quy định.

### Nếu FAIL

Validation Engine trả về danh sách lỗi có cấu trúc.

```text
Validation FAIL
      ↓
Validation Issues
      ↓
Application workflow
      ↓
DWDesignAgent
```

DWDesignAgent nhận:

```text
Requirements
+
AnalyticalRequirements
+
SchemaMetadata
+
Previous DBML
+
Validation Issues
```

và thực hiện thiết kế lại.

Workflow retry tối đa:

```text
3 lần
```

Nếu vẫn không đạt:

```text
FAILED
```

và hệ thống trả lỗi cho User.

---

# 4. Luồng chỉnh sửa Data Model

## 4.1. Chỉnh sửa DBML thủ công

Khi User sửa mã DBML trực tiếp trong editor và chọn lưu, Frontend gửi toàn bộ DBML cùng `base_revision` đã tải.

Nếu `base_revision` khớp revision hiện tại, Backend validate DBML, cập nhật trực tiếp `data_models.dbml` và tăng revision đúng 1. Luồng này không tạo `DataModelChange` và không cần Accept/Reject.

Nếu revision không khớp, Backend trả revision conflict và giữ nguyên snapshot hiện tại. Các analyzed revisions không tham gia kiểm tra conflict; chúng chỉ quyết định Data Model có `is_outdated` hay không.

## 4.2. Chỉnh sửa Data Model bằng AI Prompt

Khi User đang xem Data Model và nhập prompt, ví dụ:

```text
"Thêm DimDoctor và liên kết với FactVisit"
```

Frontend gửi:

```text
User Prompt
```

tới Backend.

Application workflow route action chỉnh sửa Data Model tới `DWDesignAgent`.

Input:

```text
Current DBML
+
User Prompt
+
Requirements
+
AnalyticalRequirements
+
SchemaMetadata
```

Luồng:

```text
Current DBML
+
Prompt
+
Requirements
+
AnalyticalRequirements
+
SchemaMetadata
      ↓
DWDesignAgent
      ↓
Proposed DBML
      ↓
ValidationEngine
```

Nếu validation thất bại:

```text
Validation Error
      ↓
Application gọi một DWDesignAgent invocation mới
```

tối đa 3 lần.

Nếu validation thành công:

```text
Proposed DBML
      ↓
data_model_changes
```

với:

```text
status = PROPOSED
base_revision = current data model revision
```

Agent **không trực tiếp ghi đè** DBML hiện tại.

User có thể:

```text
Accept
Reject
```

### Accept

Nếu:

```text
base_revision == current_revision
```

thì:

```text
proposed_dbml
      ↓
data_models.dbml

revision = revision + 1

data_model_changes.status = ACCEPTED
```

### Reject

```text
data_model_changes.status = REJECTED
```

Data Model hiện tại không thay đổi.

---

# 5. Luồng khi Requirement thay đổi

User được phép chỉnh sửa Requirement sau khi Data Model đã được tạo.

Khi User sửa Raw Requirement, hệ thống **không chạy Agent trong lúc User đang gõ**.

User phải thực hiện một hành động rõ ràng như:

```text
Save
```

hoặc:

```text
Analyze Changes
```

tùy UX được triển khai.

Luồng phân tích lại:

```text
Raw Requirement mới
      ↓
RequirementAgent
      ↓
Requirements mới
      ↓
Requirements + SchemaMetadata
      ↓
RequirementAgent
      ↓
AnalyticalRequirements mới
```

Sau khi Requirement hoặc Analytical Requirement thay đổi, Data Model hiện tại có thể không còn đồng bộ với input mới.

Hệ thống **không tự động ghi đè Data Model hiện tại**.

Data Model được hệ thống xác định tại runtime là:

```text
OUTDATED
```

Trạng thái này được tính từ revision và không được persist thành một cột trạng thái.

Frontend thông báo cho User rằng Data Model cần được cập nhật.

Ví dụ:

```text
Input đã thay đổi.
Data Model hiện tại được tạo từ dữ liệu đầu vào cũ.

[Update Data Model]
```

Khi User chọn `Update Data Model`:

```text
Requirements mới
+
AnalyticalRequirements mới
+
SchemaMetadata
      ↓
DWDesignAgent
      ↓
DBML mới
      ↓
ValidationEngine
      ↓
Optimistic revision check
      ↓
Ghi đè Data Model và tăng revision
```

Luồng regenerate này không tạo proposal. Human Review chỉ áp dụng cho AI edit từ instruction của User.

---

# 6. Luồng khi Source Data thay đổi

User được phép:

- thêm Data Source;
- thay thế Data Source;
- xóa Data Source.

Khi Source Data thay đổi, Backend tự động thực hiện lại bước deterministic:

```text
New CSV
      ↓
Parser / Profiler
      ↓
New SchemaMetadata
```

Không gọi SourceDataAgent.

Do Analytical Requirement phụ thuộc vào:

```text
Requirements
+
SchemaMetadata
```

nên khi SchemaMetadata thay đổi:

```text
AnalyticalRequirements
```

có thể không còn đồng bộ.

Hệ thống đánh dấu các kết quả downstream tương ứng là cần phân tích lại.

User có thể chọn:

```text
Analyze Changes
```

để chạy:

```text
Requirements
+
New SchemaMetadata
      ↓
RequirementAgent
      ↓
New AnalyticalRequirements
```

Sau đó Data Model hiện tại được xác định là `OUTDATED`.

Hệ thống **không tự động thay đổi DBML hiện tại**.

User chọn:

```text
Update Data Model
```

để chạy:

```text
Requirements
+
AnalyticalRequirements mới
+
SchemaMetadata mới
      ↓
DWDesignAgent
      ↓
DBML mới
      ↓
ValidationEngine
      ↓
Optimistic revision check
      ↓
Ghi đè Data Model và tăng revision
```

---

# 7. Luồng tổng thể

## Initial Generation

```text
User
 ↓
Raw Requirement ──────────────────────────────┐
                                              │
CSV                                           │
 ↓                                            │
Parser / Profiler                             │
 ↓                                            │
SchemaMetadata                                │
                                              │
Raw Requirement                              │
 ↓                                            │
RequirementAgent                              │
 ↓                                            │
Requirements                                  │
      │                                       │
      ├──────────── SchemaMetadata ────────────┘
      ↓
RequirementAgent
 ↓
AnalyticalRequirements
      │
      ├──── Requirements
      ├──── SchemaMetadata
      ↓
DWDesignAgent
 ↓
DBML
 ↓
ValidationEngine
 ├── FAIL → DWDesignAgent retry ≤ 3
 └── PASS
       ↓
Data Model
```

---

## AI Data Model Revision

```text
Current DBML
+
User Prompt
+
Requirements
+
AnalyticalRequirements
+
SchemaMetadata
      ↓
DWDesignAgent
      ↓
ValidationEngine
      ├── FAIL → retry ≤ 3
      ↓
DataModelChange
(PROPOSED)
      ↓
Human Review
 ├── Accept → DataModel revision + 1
 └── Reject → giữ DataModel hiện tại
```

---

## Requirement Change

```text
Raw Requirement changed
      ↓
RequirementAgent
      ↓
Requirements mới
      ↓
RequirementAgent
      ↓
AnalyticalRequirements mới
      ↓
Data Model OUTDATED

User chọn Update Data Model
      ↓
DWDesignAgent
      ↓
ValidationEngine
      ↓
Data Model revision + 1
```

---

## Source Data Change

```text
Source Data changed
      ↓
Parser / Profiler
      ↓
SchemaMetadata mới
      ↓
AnalyticalRequirements OUTDATED

User chọn Analyze Changes
      ↓
RequirementAgent
      ↓
AnalyticalRequirements mới
      ↓
Data Model OUTDATED

User chọn Update Data Model
      ↓
DWDesignAgent
      ↓
ValidationEngine
      ↓
Data Model revision + 1
```

---

# 8. Tóm tắt tương tác giữa các thành phần

| Nguồn                  | Đích                           | Dữ liệu / Hành động                             |
| ---------------------- | ------------------------------ | ----------------------------------------------- |
| User                   | Frontend                       | Raw Requirement / Source Data                   |
| Frontend               | Backend                        | Save / Analyze / Update / Prompt                |
| Backend                | PostgreSQL                     | Lưu Project, Raw Requirement, Data Source       |
| Backend                | File Storage                   | Lưu file CSV                                    |
| CSV Parser / Profiler  | `data_sources.schema_metadata` | Schema, Data Type, Statistics, Metadata         |
| PostgreSQL             | RequirementAgent               | Raw Requirement                                 |
| RequirementAgent       | `requirements`                 | BUSINESS / ANALYTICAL / TECHNICAL Requirements  |
| PostgreSQL             | RequirementAgent               | Requirements + SchemaMetadata                   |
| RequirementAgent       | `analytical_requirements`      | Metric / Dimension / Grain / Aggregation / Time |
| Requirements           | DWDesignAgent                  | Input nghiệp vụ                                 |
| AnalyticalRequirements | DWDesignAgent                  | Input phân tích                                 |
| SchemaMetadata         | DWDesignAgent                  | Cấu trúc và profiling dữ liệu nguồn             |
| DWDesignAgent          | ValidationEngine               | DBML                                            |
| ValidationEngine       | DWDesignAgent                  | Validation Issues khi FAIL                      |
| ValidationEngine       | Backend                        | PASS hoặc FAILED sau retry                      |
| User Prompt            | Application workflow           | Yêu cầu chỉnh sửa Data Model                    |
| Application workflow   | DWDesignAgent                  | Current DBML + Prompt + analysis input          |
| DWDesignAgent          | `data_model_changes`           | Proposed DBML sau Validation PASS               |
| Human Review           | `data_model_changes`           | ACCEPTED / REJECTED                             |
| `data_model_changes`   | `data_models`                  | Apply DBML khi Accept và revision hợp lệ        |
| `data_models`          | Data Model DDL generator       | DBML hiện tại                                   |
| Data Model service     | Frontend/User                  | DDL / SQL / Download                            |
| Data Model service     | Sandbox                        | DDL để thực thi                                 |

---

# 9. Phân chia trách nhiệm cuối cùng

```text
Application workflow
├── điều phối workflow
├── route theo User action
├── truyền input cần thiết
└── quản lý retry

RequirementAgent
├── Raw Requirement → Requirements
└── Requirements + SchemaMetadata → AnalyticalRequirements

DWDesignAgent
├── Generate Data Model
└── Revise Data Model theo User Prompt

CSV Parser / Profiler
├── Schema extraction
├── Data type inference
├── Data profiling
└── SchemaMetadata

ValidationEngine
├── DBML validation
├── Relationship validation
├── Data Warehouse design rules
└── Requirement/model consistency rules khi có

PII Guard
└── bảo vệ dữ liệu trước/sau LLM API

Human Review
└── Accept / Reject Data Model Proposal

Data Model DDL generator
└── DBML hiện hành → DDL theo target database

Sandbox
├── quản lý cấu hình và test connection theo Project
└── consume và execute DDL; không sở hữu code generation
```

`CSV Parser / Profiler` và `ValidationEngine` là các thành phần xử lý bằng code, **không phải AI Agent**.

---

# Revision và trạng thái OUTDATED

Workflow dùng integer revision, không dùng fingerprint hoặc timestamp để xác định thay đổi.

Project lưu bốn revision:

```text
requirement_revision
source_revision
analyzed_requirement_revision
analyzed_source_revision
```

- Save Raw Requirement có thay đổi làm `requirement_revision += 1`.
- UI không cho phép sửa trực tiếp một Requirement có cấu trúc; Raw Requirement vẫn là nguồn để operation cấu trúc hóa có thể tạo lại toàn bộ tập Requirements khi chạy `Analyze Changes`.
- Thêm, thay thế, upload lại, sửa SchemaMetadata hoặc xóa Data Source làm `source_revision += 1`.
- Không tăng revision khi User chỉ đang nhập trên Frontend hoặc khi thay đổi kỹ thuật không ảnh hưởng nội dung analysis.

Các trạng thái được tính trực tiếp:

```python
requirement_analysis_outdated = (
    requirement_revision != analyzed_requirement_revision
)

source_analysis_outdated = (
    source_revision != analyzed_source_revision
)
```

`Analyze Changes` chạy theo thứ tự:

```python
if requirement_analysis_outdated:
    analyze_requirements()

if requirement_analysis_outdated or source_analysis_outdated:
    analyze_analytical_requirements()
```

Chỉ sau khi các operation cần thiết thành công, hệ thống mới cập nhật analyzed revisions.
Nếu Agent thất bại, analyzed revisions không thay đổi.

Data Model lưu `generated_from_requirement_revision` và `generated_from_source_revision`. Data Model là OUTDATED khi một generated revision không khớp analyzed revision tương ứng. Giá trị `is_outdated` trong API chỉ là derived output.

Proposal chỉ lưu `base_revision` là đủ, không cần lưu revision của Requirement hoặc Source Data.
