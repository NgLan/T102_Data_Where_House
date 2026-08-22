# DATA MODEL VALIDATION ARCHITECTURE & RULE CATALOG

**Project:** AI-powered Data Warehouse Design Platform  
**Document Type:** Validation Architecture & Rule Specification  
**Status:** Proposed  
**Purpose:** Source of Truth cho việc kiểm tra Data Warehouse Model trước khi Human Review hoặc áp dụng thay đổi vào Data Model hiện tại.

---

## 1. Mục đích

Tài liệu này định nghĩa kiến trúc validation và toàn bộ rule validation cốt lõi cho Data Warehouse Model được sinh hoặc chỉnh sửa bởi `DWDesignAgent`.

Validation có bốn mục tiêu bắt buộc:

1. Phát hiện lỗi cú pháp và lỗi cấu trúc có thể xác định chắc chắn bằng code.
2. Phát hiện vi phạm các Data Warehouse design rule có thể biểu diễn deterministic.
3. Phát hiện sai lệch ngữ nghĩa giữa Requirement, Analytical Requirement, Source Metadata và Data Model bằng LLM semantic validation.
4. Tạo kết quả validation có cấu trúc, có evidence và có thể dùng lại cho retry, Human Review, UI và test.

Validation **không thay thế Human Review**. Validation là quality gate bắt buộc trước Human Review.

---

## 2. Thay đổi kiến trúc Validation

### 2.1. Kiến trúc cũ

Luồng hiện tại:

```text
DWDesignAgent
    ↓
ValidationEngine
    ├── FAIL → DWDesignAgent retry
    └── PASS → Human Review / Data Model
```

`ValidationEngine` đang được mô tả như một component code-based duy nhất, đồng thời chịu trách nhiệm kiểm tra cú pháp, relationship, Data Warehouse design rule và consistency với Requirement.

Thiết kế này chưa tách được hai loại validation có bản chất khác nhau:

- rule deterministic có thể chứng minh bằng code;
- rule semantic cần hiểu nghĩa nghiệp vụ và ngữ cảnh.

### 2.2. Kiến trúc mới

Thay `ValidationEngine` đơn khối bằng `ModelValidationService`.

```text
                         ┌──────────────────┐
                         │  DWDesignAgent   │
                         └────────┬─────────┘
                                  │ DBML
                                  ▼
                    ┌──────────────────────────┐
                    │  ModelValidationService  │
                    └────────────┬─────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
          ▼                      ▼                      ▼
┌──────────────────┐   ┌──────────────────┐   ┌─────────────────────┐
│ Structural       │   │ DWH Rule         │   │ Source Mapping      │
│ Validator        │   │ Validator        │   │ Validator           │
│ CODE             │   │ CODE             │   │ CODE                │
└────────┬─────────┘   └────────┬─────────┘   └──────────┬──────────┘
         │                      │                        │
         └──────────────────────┼────────────────────────┘
                                │ deterministic issues
                                ▼
                     ┌──────────────────────┐
                     │ Semantic Validator   │
                     │ LLM / Critic         │
                     └──────────┬───────────┘
                                │ semantic issues
                                ▼
                     ┌──────────────────────┐
                     │ ValidationAggregator │
                     │ CODE                 │
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │ ValidationPolicy     │
                     │ CODE                 │
                     └──────────┬───────────┘
                                │
                 ┌──────────────┼──────────────┐
                 ▼              ▼              ▼
               FAIL      PASS_WITH_WARNINGS   PASS
                 │              │              │
                 ▼              └──────┬───────┘
          DWDesignAgent                ▼
          retry ≤ 3              Human Review
```

### 2.3. Trách nhiệm từng thành phần

#### StructuralValidator — CODE

Chỉ kiểm tra các invariant cấu trúc có kết quả deterministic:

- DBML parse được;
- table và column không bị trùng tên trong cùng scope;
- primary key hợp lệ;
- foreign key hợp lệ;
- referenced table/column tồn tại;
- kiểu dữ liệu giữa FK và referenced key tương thích;
- relationship không bị khai báo trùng;
- object reference không bị dangling.

#### DwhRuleValidator — CODE

Kiểm tra các Data Warehouse design rule có thể biểu diễn bằng code hoặc graph rule:

- fact có grain metadata;
- fact/dimension key structure;
- fact-dimension relationship;
- date dimension requirement;
- mixed-grain structural signal;
- many-to-many không được biểu diễn sai;
- fan trap/chasm trap ở mức graph;
- SCD structure khi SCD Type 2 đã được xác định.

#### SourceMappingValidator — CODE

Kiểm tra tính tồn tại và tính nhất quán cơ bản của lineage/mapping:

- source object tồn tại;
- source column tồn tại;
- target mapping không trỏ tới object không có thật;
- datatype có khả năng chuyển đổi;
- mapping bắt buộc không bị thiếu khi workflow yêu cầu traceability.

#### SemanticValidator — LLM

Là một **Critic**, không phải agent thiết kế thứ hai.

Nhiệm vụ duy nhất là tìm lỗi hoặc rủi ro ngữ nghĩa dựa trên evidence từ:

- Requirements;
- Analytical Requirements;
- SchemaMetadata;
- Data Model;
- deterministic validation issues.

SemanticValidator **MUST NOT**:

- sửa DBML;
- tự áp dụng proposal;
- tự quyết định PASS/FAIL cuối cùng;
- tạo business fact không có evidence;
- biến suggestion chủ quan thành `ERROR` nếu không chứng minh được model không đáp ứng requirement.

#### ValidationAggregator — CODE

- merge issues từ mọi validator;
- deduplicate issues theo `code + target + evidence`;
- giữ nguyên nguồn phát hiện của issue;
- sắp xếp issue theo severity và category;
- không tự thay đổi severity do validator trả về ngoài policy được định nghĩa trong tài liệu này.

#### ValidationPolicy — CODE

Quyết định trạng thái cuối cùng:

```text
Nếu có ít nhất một ERROR  → FAIL
Nếu không có ERROR nhưng có WARNING → PASS_WITH_WARNINGS
Nếu không có issue → PASS
```

LLM không có quyền trả kết quả cuối cùng thay `ValidationPolicy`.

---

## 3. Thời điểm chạy Validation

Validation MUST chạy trong các trường hợp sau:

1. Sau khi `DWDesignAgent` sinh Data Model đầu tiên.
2. Sau mỗi lần `DWDesignAgent` retry do validation fail.
3. Sau khi `DWDesignAgent` tạo Proposed DBML từ AI Edit.
4. Sau khi sinh lại Data Model từ Requirement/Source mới trước khi ghi đè Data Model hiện tại.
5. Sau khi User chỉnh sửa DBML thủ công trước khi snapshot mới được coi là hợp lệ.
6. Sau khi User chỉnh sửa bảng trên giao diện và DBML được cập nhật.
7. Trước khi sinh DDL nếu revision Data Model hiện tại chưa có validation result tương ứng.

Validation result phải gắn với chính xác `data_model_id` và `revision` hoặc với proposal đang được validate. Không được dùng validation result của revision cũ cho revision mới.

---

## 4. Validation Context

`ModelValidationService` nhận một `ValidationContext` logic gồm:

```text
ValidationContext
├── project_id
├── data_model_id hoặc proposal_id
├── data_model_revision hoặc base_revision
├── dbml
├── requirements[]
├── analytical_requirements[]
├── schema_metadata[]
├── source_mappings[] nếu có
├── user_confirmed_business_rules[] nếu có
└── validation_mode
```

`validation_mode` có ba giá trị:

```text
INITIAL_GENERATION
CURRENT_MODEL
PROPOSAL
```

Nếu một input không tồn tại trong project thì truyền collection rỗng hoặc trạng thái `UNKNOWN`; validator không được tự dựng dữ liệu thay thế.

---

## 5. Validation Result Contract

### 5.1. ValidationStatus

```text
PASS
PASS_WITH_WARNINGS
FAIL
```

### 5.2. ValidationSeverity

```text
ERROR
WARNING
```

- `ERROR`: Có bằng chứng rằng model không hợp lệ, không nhất quán hoặc không đáp ứng một requirement bắt buộc. Issue chặn workflow.
- `WARNING`: Có rủi ro, ambiguity, design smell hoặc lựa chọn đáng review nhưng chưa đủ căn cứ để kết luận model sai. Issue không chặn Human Review.

### 5.3. ValidationCategory

```text
STRUCTURE
KEY
RELATIONSHIP
GRAIN
MEASURE
DIMENSION
TIME
REQUIREMENT_COVERAGE
SOURCE_MAPPING
BUSINESS_RULE
HISTORY
DESIGN_QUALITY
```

### 5.4. ValidatorType

```text
DETERMINISTIC
SEMANTIC
```

### 5.5. ValidationIssue

Mỗi issue MUST chứa đầy đủ các field sau:

```text
code                     stable machine-readable rule code
category                 ValidationCategory
severity                 ERROR | WARNING
validator                 DETERMINISTIC | SEMANTIC
title                    mô tả ngắn
message                  mô tả chính xác vấn đề
table_name               nullable
column_name              nullable
relationship              nullable
related_requirement_ids  danh sách, có thể rỗng
related_analytical_requirement_ids danh sách, có thể rỗng
related_source_fields     danh sách, có thể rỗng
evidence                  danh sách evidence cụ thể
recommendation            hướng sửa cụ thể, nullable khi không cần
```

Semantic issue MUST có ít nhất một `evidence`. Nếu không có evidence đủ mạnh, SemanticValidator chỉ được tạo `WARNING` hoặc không tạo issue.

---

# 6. RULE CATALOG

## 6.1. STRUCTURAL RULES — CODE

### VAL-STR-001 — DBML Syntax Must Be Valid

- **Category:** STRUCTURE
- **Validator:** DETERMINISTIC
- **Default Severity:** ERROR
- **Applies:** Mọi Data Model.
- **Input:** DBML.
- **Rule:** DBML phải parse thành công bằng parser chính thức/adapter được project sử dụng.
- **FAIL khi:** parser trả syntax error, token error, invalid declaration hoặc không tạo được AST/model structure.
- **Evidence:** parser error location và parser message.
- **Result:** Model không được chuyển sang các validator phụ thuộc AST nếu rule này fail.

### VAL-STR-002 — Table Name Must Be Unique

- **Category:** STRUCTURE
- **Validator:** DETERMINISTIC
- **Default Severity:** ERROR
- **Rule:** Trong một Data Model, hai table không được có cùng canonical name sau normalization theo quy tắc identifier của DBML parser.
- **FAIL khi:** phát hiện từ hai table trở lên có cùng canonical name.
- **Evidence:** danh sách table declarations bị trùng.

### VAL-STR-003 — Column Name Must Be Unique Within Table

- **Category:** STRUCTURE
- **Validator:** DETERMINISTIC
- **Default Severity:** ERROR
- **Rule:** Mỗi column name chỉ được xuất hiện một lần trong cùng một table.
- **FAIL khi:** một table có từ hai column trở lên có cùng canonical name.
- **Evidence:** table name và các column declaration bị trùng.

### VAL-STR-004 — Referenced Table Must Exist

- **Category:** RELATIONSHIP
- **Validator:** DETERMINISTIC
- **Default Severity:** ERROR
- **Rule:** Mọi relationship/FK phải trỏ đến một table tồn tại trong model.
- **FAIL khi:** `reference_table` không tồn tại.
- **Evidence:** relationship declaration và missing table name.

### VAL-STR-005 — Referenced Column Must Exist

- **Category:** RELATIONSHIP
- **Validator:** DETERMINISTIC
- **Default Severity:** ERROR
- **Rule:** Mọi relationship/FK phải trỏ đến một column tồn tại trong referenced table.
- **FAIL khi:** table tồn tại nhưng referenced column không tồn tại.
- **Evidence:** source field, target table và missing target column.

### VAL-STR-006 — Relationship Must Not Be Duplicated

- **Category:** RELATIONSHIP
- **Validator:** DETERMINISTIC
- **Default Severity:** ERROR
- **Rule:** Không được khai báo lặp cùng một logical relationship giữa cùng source column và target column với cùng direction/cardinality.
- **FAIL khi:** tồn tại từ hai relationship declaration tương đương trở lên.
- **Evidence:** các relationship declaration bị trùng.

### VAL-STR-007 — Key Data Types Must Be Compatible

- **Category:** KEY
- **Validator:** DETERMINISTIC
- **Default Severity:** ERROR
- **Rule:** Foreign key và referenced key phải có datatype bằng nhau hoặc thuộc compatibility matrix được project cho phép.
- **FAIL khi:** datatype không có conversion an toàn theo compatibility matrix.
- **Evidence:** source column datatype và referenced column datatype.

### VAL-STR-008 — Primary Key Columns Must Exist

- **Category:** KEY
- **Validator:** DETERMINISTIC
- **Default Severity:** ERROR
- **Rule:** Mọi column được khai báo thuộc primary key phải tồn tại trong chính table đó.
- **FAIL khi:** PK metadata/index reference một column không tồn tại.
- **Evidence:** table name, PK declaration và missing column.

### VAL-STR-009 — Table Must Have A Primary Key

- **Category:** KEY
- **Validator:** DETERMINISTIC
- **Default Severity:** ERROR
- **Rule:** Mọi Fact Table và Dimension Table chính thức trong dimensional model phải có primary key.
- **FAIL khi:** table được phân loại là FACT hoặc DIMENSION nhưng không có PK.
- **Evidence:** table classification và key metadata.

---

## 6.2. GRAIN & FACT RULES

### VAL-GRN-001 — Fact Table Must Declare Grain

- **Category:** GRAIN
- **Validator:** DETERMINISTIC
- **Default Severity:** ERROR
- **Rule:** Mỗi Fact Table phải có grain được biểu diễn rõ trong model metadata/note hoặc structured design representation mà validator đọc được.
- **FAIL khi:** Fact Table không có grain hoặc grain rỗng.
- **Evidence:** fact table name và missing grain field.

### VAL-GRN-002 — Fact Grain Must Represent One Atomic Row Meaning

- **Category:** GRAIN
- **Validator:** SEMANTIC
- **Default Severity:** ERROR
- **Rule:** Grain phải mô tả chính xác một dòng của Fact đại diện cho một business event/snapshot/accumulating process ở một mức chi tiết duy nhất.
- **FAIL khi:** grain đồng thời mô tả nhiều row meanings không tương thích hoặc không thể xác định một row đại diện cho gì.
- **Evidence required:** grain text + relevant Analytical Requirement hoặc design metadata.

### VAL-GRN-003 — Fact Grain Must Match Analytical Requirement

- **Category:** GRAIN
- **Validator:** SEMANTIC
- **Default Severity:** ERROR
- **Rule:** Grain của Fact phải đủ chi tiết để trả lời các Analytical Requirement mà Fact đó phục vụ.
- **FAIL khi:** model aggregate dữ liệu lên mức cao hơn làm mất khả năng trả lời requirement hoặc dùng grain chi tiết/khác nghĩa không phù hợp với business process.
- **Evidence required:** Analytical Requirement grain + Fact grain + source identifier/time evidence nếu có.

### VAL-GRN-004 — Measures Must Share The Fact Grain

- **Category:** GRAIN
- **Validator:** SEMANTIC
- **Default Severity:** ERROR
- **Rule:** Tất cả measure trong cùng Fact phải có ý nghĩa tại cùng grain của Fact.
- **FAIL khi:** ít nhất một measure thuộc một event/level khác và việc lưu chung tạo mixed grain.
- **Evidence required:** fact grain + measure meanings + related Analytical Requirements.

### VAL-GRN-005 — Fact Key Structure Must Be Consistent With Declared Grain

- **Category:** GRAIN
- **Validator:** SEMANTIC
- **Default Severity:** ERROR
- **Rule:** Primary key hoặc uniqueness structure của Fact phải có khả năng phân biệt các row theo grain đã khai báo.
- **FAIL khi:** key structure cho phép hai row cùng grain identity nhưng không có discriminator hợp lệ, hoặc key thể hiện một grain khác với grain text.
- **Evidence required:** grain + PK/unique structure + dimensional keys/event identifier.

### VAL-GRN-006 — Fact Must Represent A Recognizable Business Process

- **Category:** GRAIN
- **Validator:** SEMANTIC
- **Default Severity:** ERROR
- **Rule:** Fact phải có business process hoặc measurement process có căn cứ từ Requirement, Analytical Requirement hoặc Source Data.
- **FAIL khi:** Fact được tạo nhưng không thể liên hệ với bất kỳ process/metric requirement/source event nào.
- **Evidence required:** Fact identity + absence/conflict evidence trong project context.

---

## 6.3. MEASURE RULES

### VAL-MEA-001 — Required Metric Must Have A Measure Or Derivable Expression

- **Category:** MEASURE
- **Validator:** SEMANTIC
- **Default Severity:** ERROR
- **Rule:** Mỗi metric/KPI trong Analytical Requirement phải được hỗ trợ bởi một stored measure hoặc một derivable expression có đủ input trong model.
- **FAIL khi:** không có measure/expression nào có thể tạo metric yêu cầu.
- **Evidence required:** Analytical Requirement metric + model measures/columns.

### VAL-MEA-002 — Measure Meaning Must Match Metric Meaning

- **Category:** MEASURE
- **Validator:** SEMANTIC
- **Default Severity:** ERROR
- **Rule:** Measure được dùng để đáp ứng metric phải có cùng business meaning, không chỉ giống tên.
- **FAIL khi:** metric và measure có semantic khác nhau, đơn vị khác nhau hoặc đại diện sự kiện khác nhau.
- **Evidence required:** requirement/metric wording + measure/source meaning.

### VAL-MEA-003 — Aggregation Method Must Be Semantically Valid

- **Category:** MEASURE
- **Validator:** SEMANTIC
- **Default Severity:** ERROR
- **Rule:** Aggregation Method trong Analytical Requirement phải phù hợp với bản chất measure và grain.
- **FAIL khi:** sử dụng aggregation làm sai nghĩa metric, ví dụ cộng một tỷ lệ đã aggregate, SUM một giá trị không additive, hoặc COUNT sai business entity.
- **Evidence required:** aggregation method + measure meaning + grain.

### VAL-MEA-004 — Measure Data Type Must Support Required Aggregation

- **Category:** MEASURE
- **Validator:** DETERMINISTIC
- **Default Severity:** ERROR
- **Rule:** Datatype vật lý của measure phải hỗ trợ operation được yêu cầu.
- **FAIL khi:** operation yêu cầu numeric/date semantics nhưng column datatype không tương thích.
- **Evidence:** column datatype và required aggregation.

### VAL-MEA-005 — Derived Measure Inputs Must Exist

- **Category:** MEASURE
- **Validator:** DETERMINISTIC
- **Default Severity:** ERROR
- **Rule:** Nếu metric/measure có expression được lưu trong structured metadata, mọi referenced input column phải tồn tại trong model hoặc source mapping được khai báo.
- **FAIL khi:** expression reference missing field.
- **Evidence:** expression và missing fields.

---

## 6.4. DIMENSION & TIME RULES

### VAL-DIM-001 — Required Analytical Dimension Must Be Represented

- **Category:** DIMENSION
- **Validator:** SEMANTIC
- **Default Severity:** ERROR
- **Rule:** Mỗi dimension được yêu cầu trong Analytical Requirement phải có Dimension Table, degenerate dimension hoặc attribute path hợp lệ cho phép slice/filter/group theo dimension đó.
- **FAIL khi:** model không cung cấp đường phân tích cho dimension yêu cầu.
- **Evidence required:** Analytical Requirement dimension + relevant model path.

### VAL-DIM-002 — Dimension Must Have A Stable Warehouse Key

- **Category:** KEY
- **Validator:** DETERMINISTIC
- **Default Severity:** ERROR
- **Rule:** Dimension Table phải có một PK ổn định dùng làm warehouse key. Nếu model metadata phân biệt `surrogate_key`, key đó phải tồn tại và là PK/unique key phù hợp.
- **FAIL khi:** Dimension không có key hoặc declared surrogate key không tồn tại/không unique.
- **Evidence:** dimension key metadata.

### VAL-DIM-003 — Dimension Must Contain Descriptive Context

- **Category:** DIMENSION
- **Validator:** SEMANTIC
- **Default Severity:** WARNING
- **Rule:** Dimension không nên chỉ chứa surrogate key và foreign key; nó phải cung cấp descriptive attributes hoặc có lý do rõ ràng để tồn tại.
- **WARN khi:** Dimension không thêm context phân tích hữu ích và có dấu hiệu là wrapper kỹ thuật không cần thiết.
- **Evidence required:** dimension columns + linked Analytical Requirements.

### VAL-DIM-004 — Fact-to-Dimension Relationship Must Exist For Used Dimension

- **Category:** RELATIONSHIP
- **Validator:** DETERMINISTIC
- **Default Severity:** ERROR
- **Rule:** Khi Fact metadata khai báo sử dụng một Dimension hoặc Analytical mapping gán dimension cho Fact, phải tồn tại relationship path hợp lệ từ Fact đến Dimension.
- **FAIL khi:** dimension được khai báo dùng bởi Fact nhưng không có relationship path.
- **Evidence:** Fact, Dimension và graph path result.

### VAL-TIM-001 — Required Time Analysis Must Have A Time Path

- **Category:** TIME
- **Validator:** SEMANTIC
- **Default Severity:** ERROR
- **Rule:** Analytical Requirement có time granularity phải được model hỗ trợ bằng date/time key hoặc timestamp path có khả năng group theo granularity đó.
- **FAIL khi:** requirement yêu cầu phân tích theo thời gian nhưng model không có time attribute/path phù hợp.
- **Evidence required:** required time granularity + model time fields.

### VAL-TIM-002 — Required Date Dimension Must Be Connected To Fact

- **Category:** TIME
- **Validator:** DETERMINISTIC
- **Default Severity:** ERROR
- **Applies:** Khi design metadata quy định dùng Date Dimension cho Analytical Requirement tương ứng.
- **Rule:** Fact phải có FK/relationship hợp lệ tới Date Dimension.
- **FAIL khi:** Date Dimension tồn tại nhưng Fact cần phân tích theo date không kết nối tới Date Dimension.
- **Evidence:** Fact, date dimension, relationship graph.

### VAL-TIM-003 — Multiple Date Roles Must Be Unambiguous

- **Category:** TIME
- **Validator:** SEMANTIC
- **Default Severity:** WARNING
- **Rule:** Nếu một Fact có nhiều date/time meaning như order date, ship date, discharge date, payment date, relationship/role phải đủ rõ để không nhập nhằng semantic.
- **WARN khi:** nhiều FK cùng trỏ Date Dimension nhưng tên/role metadata không cho biết business meaning.
- **Evidence required:** date keys + requirement/source meanings.

---

## 6.5. RELATIONSHIP & GRAPH RULES

### VAL-REL-001 — Fact-to-Dimension Cardinality Must Be Plausible

- **Category:** RELATIONSHIP
- **Validator:** DETERMINISTIC + SEMANTIC
- **Default Severity:** ERROR
- **Rule:** Một Fact row thông thường phải reference tối đa một member của từng Dimension role; relationship metadata không được mô tả sai thành Dimension-to-Fact one-to-one hoặc fact-side one-to-many nếu không có bridge/design justification.
- **FAIL khi:** deterministic graph cho thấy cardinality bất khả thi hoặc semantic context xác nhận cardinality trái business meaning.
- **Evidence:** relationship cardinality + key constraints + context nếu semantic.

### VAL-REL-002 — Direct Many-To-Many Fact-Dimension Relationship Requires Bridge

- **Category:** RELATIONSHIP
- **Validator:** DETERMINISTIC
- **Default Severity:** ERROR
- **Rule:** Relationship many-to-many trực tiếp giữa Fact và Dimension không được biểu diễn chỉ bằng một FK đơn. Model phải có bridge/association structure hoặc structured resolution tương ứng.
- **FAIL khi:** graph/cardinality khai báo many-to-many nhưng không có bridge/resolution structure.
- **Evidence:** graph path và participating tables.

### VAL-REL-003 — Fan Trap Must Be Detected

- **Category:** RELATIONSHIP
- **Validator:** DETERMINISTIC
- **Default Severity:** ERROR
- **Rule:** Graph validator phải phát hiện pattern trong đó một parent/detail path làm một measure có nguy cơ bị nhân bản khi join qua hai one-to-many branches ở grain không tương thích.
- **FAIL khi:** tồn tại join path có thể nhân measure và không có bridge/pre-aggregation/grain boundary giải quyết.
- **Evidence:** graph path, cardinalities và affected Fact/measure.

### VAL-REL-004 — Chasm Trap Must Be Detected

- **Category:** RELATIONSHIP
- **Validator:** DETERMINISTIC
- **Default Severity:** ERROR
- **Rule:** Graph validator phải phát hiện trường hợp nhiều Fact/process độc lập cùng nối qua Dimension chung theo cách một query join xuyên các Fact có thể tạo Cartesian multiplication hoặc ambiguity ở grain.
- **FAIL khi:** model có multi-fact join path nguy hiểm và không có conformed-dimension/drill-across boundary hoặc aggregation rule rõ ràng.
- **Evidence:** Fact paths, shared dimensions và cardinalities.

### VAL-REL-005 — Relationship Cycle Must Be Reviewable

- **Category:** RELATIONSHIP
- **Validator:** DETERMINISTIC
- **Default Severity:** WARNING
- **Rule:** Relationship graph có cycle phải được cảnh báo vì có thể tạo ambiguous join path.
- **WARN khi:** phát hiện cycle giữa các tables trong analytical model.
- **Evidence:** cycle path.
- **Escalation:** SemanticValidator có thể nâng thành ERROR chỉ khi evidence chứng minh cycle làm requirement không thể query đúng.

### VAL-REL-006 — Fact-To-Fact Direct Relationship Requires Explicit Justification

- **Category:** RELATIONSHIP
- **Validator:** SEMANTIC
- **Default Severity:** WARNING
- **Rule:** Fact Table không nên trực tiếp phụ thuộc Fact Table khác nếu cùng kết quả có thể biểu diễn bằng conformed dimensions hoặc process-specific mapping.
- **WARN khi:** có direct fact-to-fact relationship.
- **ERROR khi:** relationship làm trộn grain hoặc tạo double counting có evidence rõ.
- **Evidence required:** fact grains + relationship + affected metrics.

---

## 6.6. REQUIREMENT COVERAGE RULES

### VAL-REQ-001 — Every Analytical Requirement Must Be Traceable To Model Elements

- **Category:** REQUIREMENT_COVERAGE
- **Validator:** SEMANTIC
- **Default Severity:** ERROR
- **Rule:** Mỗi Analytical Requirement phải trace được tối thiểu tới Fact/process, metric/measure và các dimensions/time path cần thiết.
- **FAIL khi:** không xác định được model elements đủ để trả lời Analytical Requirement.
- **Evidence required:** Analytical Requirement + missing/available model elements.

### VAL-REQ-002 — High Priority Requirement Must Not Be Missing

- **Category:** REQUIREMENT_COVERAGE
- **Validator:** SEMANTIC
- **Default Severity:** ERROR
- **Rule:** Requirement `HIGH` có nội dung liên quan trực tiếp đến Data Warehouse Design phải được model đáp ứng hoặc được biểu diễn là unresolved/blocking.
- **FAIL khi:** requirement HIGH bị bỏ qua mà không có unresolved status.
- **Evidence required:** requirement ID/priority + model coverage result.

### VAL-REQ-003 — Business Requirement Must Have At Least One Supporting Analytical Path

- **Category:** REQUIREMENT_COVERAGE
- **Validator:** SEMANTIC
- **Default Severity:** WARNING
- **Rule:** Business Requirement có mục tiêu phân tích phải liên kết được tới ít nhất một Analytical Requirement và model path.
- **WARN khi:** business goal tồn tại nhưng không thấy analytical path cụ thể.
- **ERROR khi:** requirement đã được xác nhận là mandatory output nhưng model hoàn toàn không thể hỗ trợ.
- **Evidence required:** business requirement + analytical/model trace.

### VAL-REQ-004 — Technical Requirement Affecting Schema Must Be Enforced

- **Category:** BUSINESS_RULE
- **Validator:** DETERMINISTIC hoặc SEMANTIC tùy rule
- **Default Severity:** ERROR
- **Rule:** Technical Requirement đã structured/confirmed và ảnh hưởng trực tiếp schema phải được phản ánh trong model.
- **FAIL khi:** model vi phạm explicit technical requirement như mandatory key, required anonymized field handling, prohibited attribute hoặc required datatype/constraint.
- **Evidence:** requirement ID + affected schema elements.

### VAL-REQ-005 — Model Must Not Introduce Unsupported Business Assumptions

- **Category:** BUSINESS_RULE
- **Validator:** SEMANTIC
- **Default Severity:** ERROR
- **Rule:** Model không được đưa một business rule, KPI meaning, relationship meaning hoặc classification thành fact nếu không có căn cứ từ User-confirmed input, Requirement, Analytical Requirement hoặc Source evidence.
- **FAIL khi:** assumption mới làm thay đổi meaning/behavior của model và được trình bày như fact.
- **Evidence required:** unsupported model statement + absence/conflict in authoritative context.

---

## 6.7. SOURCE MAPPING & GROUNDING RULES

### VAL-SRC-001 — Referenced Source Table Must Exist

- **Category:** SOURCE_MAPPING
- **Validator:** DETERMINISTIC
- **Default Severity:** ERROR
- **Rule:** Mọi source-to-target mapping tới source table phải trỏ tới table tồn tại trong `SchemaMetadata`.
- **FAIL khi:** source table không tồn tại.
- **Evidence:** mapping + available source tables.

### VAL-SRC-002 — Referenced Source Column Must Exist

- **Category:** SOURCE_MAPPING
- **Validator:** DETERMINISTIC
- **Default Severity:** ERROR
- **Rule:** Mọi mapped source column phải tồn tại trong đúng source table.
- **FAIL khi:** source column không tồn tại.
- **Evidence:** mapping + source schema.

### VAL-SRC-003 — Required Target Field Must Have Source Or Explicit Derivation

- **Category:** SOURCE_MAPPING
- **Validator:** DETERMINISTIC
- **Default Severity:** ERROR
- **Applies:** Khi workflow yêu cầu source-to-target traceability.
- **Rule:** Mỗi target field bắt buộc phục vụ key/measure/required dimension attribute phải có source mapping hoặc derivation expression.
- **FAIL khi:** target field không có source và không có derivation.
- **Evidence:** target field + missing mapping.

### VAL-SRC-004 — Source And Target Data Types Must Be Transformable

- **Category:** SOURCE_MAPPING
- **Validator:** DETERMINISTIC
- **Default Severity:** ERROR
- **Rule:** Source datatype phải convert được sang target datatype theo compatibility/conversion matrix.
- **FAIL khi:** conversion không hợp lệ hoặc có nguy cơ mất nghĩa chắc chắn mà không có explicit transform.
- **Evidence:** source datatype, target datatype, transform metadata.

### VAL-SRC-005 — Source Mapping Meaning Must Be Semantically Compatible

- **Category:** SOURCE_MAPPING
- **Validator:** SEMANTIC
- **Default Severity:** ERROR
- **Rule:** Source field được map sang target field phải có business meaning tương thích, không chỉ datatype hoặc tên gần giống.
- **FAIL khi:** mapping làm đổi nghĩa entity/measure/dimension.
- **Evidence required:** source metadata/sample meaning + target meaning + requirement context.

### VAL-SRC-006 — Source Key Assumption Must Be Grounded

- **Category:** SOURCE_MAPPING
- **Validator:** SEMANTIC
- **Default Severity:** WARNING
- **Rule:** Một source field chỉ được coi là business key/unique identifier chắc chắn khi source metadata, constraint, profiling đủ mạnh hoặc User/Requirement xác nhận.
- **WARN khi:** model dựa vào inferred uniqueness từ sample data nhưng không có official constraint/confirmation.
- **ERROR khi:** source evidence trực tiếp mâu thuẫn với key assumption.
- **Evidence required:** source constraint/profiling + key usage.

### VAL-SRC-007 — Source Relationship Assumption Must Be Grounded

- **Category:** SOURCE_MAPPING
- **Validator:** SEMANTIC
- **Default Severity:** WARNING
- **Rule:** Relationship business meaning giữa source entities phải dựa trên FK metadata, matching keys có căn cứ, Requirement hoặc User confirmation.
- **WARN khi:** relationship chỉ được suy ra từ tên column mà không có evidence mạnh.
- **ERROR khi:** source metadata xác nhận relationship khác với model.
- **Evidence required:** source relationship evidence + model relationship.

---

## 6.8. HISTORY / SCD RULES

### VAL-HIS-001 — Historical Requirement Must Have A History Strategy

- **Category:** HISTORY
- **Validator:** SEMANTIC
- **Default Severity:** ERROR
- **Rule:** Nếu Requirement/Analytical Requirement yêu cầu phân tích lịch sử theo trạng thái/thuộc tính dimension tại thời điểm sự kiện, model phải có history strategy rõ ràng.
- **FAIL khi:** requirement cần historical correctness nhưng Dimension bị overwrite mà không có versioning/effective dating phù hợp.
- **Evidence required:** historical requirement + dimension structure/strategy.

### VAL-HIS-002 — SCD Type 2 Structure Must Be Complete

- **Category:** HISTORY
- **Validator:** DETERMINISTIC
- **Default Severity:** ERROR
- **Applies:** Khi Dimension được khai báo dùng SCD Type 2.
- **Rule:** Dimension SCD2 phải có surrogate warehouse key và các field đủ để xác định hiệu lực version. Tối thiểu phải có `effective_from` và `effective_to`. Nếu project dùng tên vật lý khác, hai field đó phải được gắn semantic role `EFFECTIVE_FROM` và `EFFECTIVE_TO` trong structured metadata.
- **FAIL khi:** thiếu warehouse key hoặc thiếu effective period boundary.
- **Evidence:** SCD metadata + dimension columns.

### VAL-HIS-003 — SCD Type 2 Version Interval Must Be Non-Ambiguous

- **Category:** HISTORY
- **Validator:** DETERMINISTIC
- **Default Severity:** ERROR
- **Applies:** Khi Dimension dùng SCD Type 2.
- **Rule:** Model metadata phải xác định được interval semantics của version; `effective_from` và `effective_to` không được cùng nullable theo cách khiến không phân biệt được version hiện hành, trừ khi có field được gắn semantic role `IS_CURRENT` trong structured metadata.
- **FAIL khi:** không có cách deterministic xác định current/effective version.
- **Evidence:** SCD columns/constraints.

---

## 6.9. DESIGN QUALITY RULES

### VAL-QLT-001 — Redundant Dimension Should Be Reported

- **Category:** DESIGN_QUALITY
- **Validator:** SEMANTIC
- **Default Severity:** WARNING
- **Rule:** Dimension không phục vụ Requirement, Analytical Requirement, reusable descriptive context hoặc history requirement phải được cảnh báo là có khả năng dư thừa.
- **WARN khi:** không tìm thấy purpose có evidence cho Dimension.
- **Evidence required:** dimension + coverage search result.

### VAL-QLT-002 — Redundant Fact Should Be Reported

- **Category:** DESIGN_QUALITY
- **Validator:** SEMANTIC
- **Default Severity:** WARNING
- **Rule:** Fact không phục vụ metric/process requirement nào và không có source business event riêng phải được cảnh báo.
- **WARN khi:** không có requirement/process/metric mapping cho Fact.
- **Evidence required:** Fact + traceability result.

### VAL-QLT-003 — Duplicate Semantic Dimension Must Be Reported

- **Category:** DESIGN_QUALITY
- **Validator:** SEMANTIC
- **Default Severity:** WARNING
- **Rule:** Hai Dimension biểu diễn cùng business entity và cùng analytical role nhưng không có lý do history/security/role-playing khác nhau phải được cảnh báo.
- **WARN khi:** semantic overlap cao và không có explicit distinction.
- **Evidence required:** dimension meanings + attributes + linked requirements.

### VAL-QLT-004 — Unnecessary Snowflaking Must Be Reported

- **Category:** DESIGN_QUALITY
- **Validator:** SEMANTIC
- **Default Severity:** WARNING
- **Rule:** Chuỗi Dimension-to-Dimension normalization làm tăng join complexity nhưng không có requirement tái sử dụng, hierarchy, history hoặc governance hỗ trợ phải được cảnh báo.
- **WARN khi:** snowflake branch không có design justification trong project context.
- **Evidence required:** graph branch + attributes + requirement context.

---

# 7. Severity Escalation Rules

SemanticValidator chỉ được nâng một issue từ `WARNING` lên `ERROR` khi thỏa cả ba điều kiện:

1. Có evidence cụ thể từ Requirement, Analytical Requirement, User-confirmed Business Rule hoặc Source Metadata.
2. Có thể chỉ ra chính xác model element gây sai lệch.
3. Có thể giải thích model mất khả năng trả lời requirement, tạo kết quả sai hoặc vi phạm rule bắt buộc như thế nào.

Nếu thiếu một trong ba điều kiện, severity tối đa là `WARNING`.

Deterministic rule có severity cố định theo catalog, trừ rule có ghi rõ escalation riêng.

---

# 8. Semantic Validator Output Rules

SemanticValidator MUST trả structured output theo schema đã định nghĩa, không trả prose tự do làm kết quả chính.

Mỗi semantic issue phải:

- dùng một `ValidationIssueCode` đã đăng ký;
- không tự tạo code ngẫu nhiên;
- nêu target table/column/relationship khi xác định được;
- tham chiếu ID của Requirement/Analytical Requirement liên quan;
- đưa evidence cụ thể;
- phân biệt `observed source fact`, `user-confirmed fact`, `inference`;
- không coi sample statistic là business constraint;
- không coi tên column giống nhau là bằng chứng duy nhất cho semantic equivalence;
- không coi output trước đó của `DWDesignAgent` là authoritative evidence.

---

# 9. Validation Execution Order

Validation chạy theo thứ tự cố định:

```text
1. Parse DBML
2. Structural Rules
3. Key Rules
4. Relationship Graph Rules
5. Deterministic DWH Rules
6. Source Mapping Rules
7. Semantic Rules
8. Aggregate Issues
9. Apply Validation Policy
```

Nếu `VAL-STR-001` fail, không chạy validator cần AST/graph. Kết quả trả `FAIL` ngay với syntax issues.

Nếu structural validation có ERROR khác nhưng AST vẫn usable, hệ thống MAY tiếp tục các deterministic validator độc lập để trả nhiều issue trong một lượt. SemanticValidator chỉ được gọi khi context model đủ parse để review có nghĩa.

---

# 10. Retry Policy

Khi kết quả là `FAIL` trong workflow do Agent tạo model:

```text
Validation Issues
      ↓
Supervisor
      ↓
DWDesignAgent
      ↓
Revised DBML
      ↓
ModelValidationService
```

Tối đa **3 lần retry** cho cùng một generation/revision workflow.

Mỗi retry phải truyền:

- DBML trước đó;
- toàn bộ ERROR issues;
- WARNING issues liên quan trực tiếp đến ERROR hoặc design target;
- Requirement/Analytical Requirement/SchemaMetadata gốc.

`DWDesignAgent` không được bỏ qua ERROR issue mà không sửa hoặc giải thích bằng output structured được workflow cho phép.

Sau 3 lần vẫn có ERROR:

```text
Workflow Status = FAILED
```

Không tự động lưu model đó làm approved/current valid model.

---

# 11. Human Review Policy

### PASS

- Cho phép chuyển trực tiếp sang Human Review.
- UI hiển thị không có validation issue blocking.

### PASS_WITH_WARNINGS

- Cho phép Human Review.
- UI phải hiển thị warnings.
- User có quyền Accept nếu workflow cho phép.
- Warning không tự động làm proposal `CONFLICTED` hoặc `REJECTED`.

### FAIL

- Không cho phép tự động Accept/Apply như một valid model.
- Với Agent workflow: retry theo Retry Policy.
- Với manual edit: trả validation issues cho User để sửa; không làm mất snapshot/revision hiện tại đã hợp lệ trước đó.

---

# 12. Validation And Data Model Revision

Validation result phải thuộc một snapshot cụ thể.

```text
DataModel revision N
        ↓
ValidationResult for revision N
```

Khi DBML thay đổi và revision tăng:

```text
revision N validation result
≠
revision N+1 validation result
```

Không được tái sử dụng `PASS` của revision cũ cho revision mới.

Proposal validation phải gắn với:

```text
proposal_id
base_revision
proposed_dbml_sha256 (SHA-256 của nội dung `proposed_dbml`)
```

Nếu proposal content thay đổi thì phải validate lại.

---

# 13. API / DTO Changes Required

`DataModelValidationIssueResponse` hiện tại cần mở rộng để hỗ trợ kiến trúc này.

Đề xuất contract:

```text
code: ValidationIssueCode
category: ValidationCategory
severity: ValidationSeverity
validator: ValidatorType
table_name: string | null
column_name: string | null
relationship: string | null
title: string
message: string
related_requirement_ids: string[]
related_analytical_requirement_ids: string[]
related_source_fields: string[]
evidence: ValidationEvidence[]
recommendation: string | null
```

Validation summary nên có:

```text
status: PASS | PASS_WITH_WARNINGS | FAIL
revision: integer
error_count: integer
warning_count: integer
issues: ValidationIssue[]
validated_at: datetime
```

API không nên chỉ trả `list[DataModelValidationIssueResponse]` nếu Frontend cần biết trạng thái tổng thể. Nên có một payload summary chứa `status` và `issues`.

---

# 14. ValidationIssueCode Registry

Các code bắt buộc của catalog này:

```text
DBML_SYNTAX_INVALID
TABLE_NAME_DUPLICATED
TABLE_COLUMN_NAME_DUPLICATED
REFERENCED_TABLE_NOT_FOUND
REFERENCED_COLUMN_NOT_FOUND
RELATIONSHIP_DUPLICATED
KEY_DATA_TYPE_INCOMPATIBLE
PRIMARY_KEY_COLUMN_NOT_FOUND
TABLE_PRIMARY_KEY_MISSING
FACT_GRAIN_MISSING
FACT_GRAIN_AMBIGUOUS
FACT_GRAIN_REQUIREMENT_MISMATCH
FACT_MIXED_GRAIN_MEASURES
FACT_KEY_GRAIN_MISMATCH
FACT_BUSINESS_PROCESS_UNGROUNDED
REQUIRED_METRIC_MISSING
MEASURE_SEMANTIC_MISMATCH
AGGREGATION_METHOD_INVALID
MEASURE_DATA_TYPE_INVALID
DERIVED_MEASURE_INPUT_MISSING
REQUIRED_DIMENSION_MISSING
DIMENSION_WAREHOUSE_KEY_INVALID
DIMENSION_DESCRIPTIVE_CONTEXT_MISSING
FACT_DIMENSION_RELATIONSHIP_MISSING
TIME_ANALYSIS_PATH_MISSING
DATE_DIMENSION_RELATIONSHIP_MISSING
DATE_ROLE_AMBIGUOUS
FACT_DIMENSION_CARDINALITY_INVALID
MANY_TO_MANY_BRIDGE_MISSING
FAN_TRAP_DETECTED
CHASM_TRAP_DETECTED
RELATIONSHIP_CYCLE_DETECTED
FACT_TO_FACT_RELATIONSHIP_RISK
ANALYTICAL_REQUIREMENT_NOT_COVERED
HIGH_PRIORITY_REQUIREMENT_NOT_COVERED
BUSINESS_REQUIREMENT_ANALYTICAL_PATH_MISSING
TECHNICAL_REQUIREMENT_VIOLATED
UNSUPPORTED_BUSINESS_ASSUMPTION
SOURCE_TABLE_NOT_FOUND
SOURCE_COLUMN_NOT_FOUND
TARGET_SOURCE_MAPPING_MISSING
SOURCE_TARGET_DATA_TYPE_INCOMPATIBLE
SOURCE_MAPPING_SEMANTIC_MISMATCH
SOURCE_KEY_UNGROUNDED
SOURCE_RELATIONSHIP_UNGROUNDED
HISTORY_STRATEGY_MISSING
SCD2_STRUCTURE_INCOMPLETE
SCD2_INTERVAL_AMBIGUOUS
REDUNDANT_DIMENSION
REDUNDANT_FACT
DUPLICATE_SEMANTIC_DIMENSION
UNNECESSARY_SNOWFLAKING
```

Mỗi code chỉ có một định nghĩa canonical trong catalog. Không được dùng hai code khác nhau cho cùng một rule.

---

# 15. Rule Configuration Policy

Rule catalog là source of truth về nghĩa của rule.

Implementation có thể có config để enable/disable rule theo project mode, nhưng:

- không được đổi meaning của rule bằng config;
- không được đổi `ERROR` thành `WARNING` tùy tiện ở runtime;
- rule bắt buộc trong catalog không được disable nếu workflow tương ứng cần nó;
- rule conditional chỉ chạy khi `Applies` condition thỏa;
- config phải dùng stable rule code.

---

# 16. Testing Requirements For Validation

Mỗi deterministic rule MUST có:

1. ít nhất một positive test;
2. ít nhất một negative test;
3. boundary test khi rule có cardinality/datatype/graph condition;
4. test đảm bảo issue code và severity đúng;
5. test đảm bảo evidence/target đúng.

Mỗi semantic rule MUST có evaluation dataset tối thiểu gồm:

1. valid model không được tạo false ERROR;
2. invalid model phải phát hiện issue mong muốn;
3. ambiguous model chỉ được WARNING nếu thiếu evidence;
4. adversarial naming case để tránh chỉ match theo tên column/table;
5. conflict case giữa source và requirement;
6. missing-context case để đảm bảo model không tự suy diễn fact.

SemanticValidator phải được đánh giá riêng bằng precision/recall hoặc rule-level detection rate trên bộ case cố định trước khi thay model/prompt.

---

# 17. Observability

Mỗi validation run phải ghi nhận tối thiểu:

```text
validation_run_id
project_id
data_model_id hoặc proposal_id
revision/base_revision
status
error_count
warning_count
rules_executed
rules_skipped
semantic_validator_model nếu có
semantic_validator_latency_ms nếu có
created_at
```

Application log không lưu full sensitive source data hoặc full LLM prompt/response. LLM tracing sử dụng observability layer riêng theo coding guideline của project.

---

# 18. Final Workflow

## Initial Generation

```text
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
ModelValidationService
        ├── FAIL → retry ≤ 3
        ├── PASS_WITH_WARNINGS
        └── PASS
                ↓
           Data Model / Human Review
```

## AI Edit Proposal

```text
Current DBML
+
User Instruction
+
Project Context
        ↓
DWDesignAgent
        ↓
Proposed DBML
        ↓
ModelValidationService
        ├── FAIL → retry ≤ 3
        └── PASS / PASS_WITH_WARNINGS
                ↓
        DataModelChange(PROPOSED)
                ↓
           Human Review
```

## Manual Edit

```text
Current DBML revision N
        ↓
User edits DBML/UI
        ↓
New DBML
        ↓
ModelValidationService
        ├── FAIL → return issues, do not replace valid snapshot
        └── PASS / PASS_WITH_WARNINGS
                ↓
        optimistic revision check
                ↓
        save revision N+1
```

---

# 19. Architectural Decisions

Các quyết định được chốt trong tài liệu này:

1. Validation sử dụng **hybrid architecture**, không chọn riêng code hoặc riêng LLM.
2. Syntax, structure, key, graph và deterministic DWH invariants dùng **code**.
3. Grain semantics, measure semantics, requirement coverage, business meaning và source semantic mapping dùng **LLM SemanticValidator**.
4. SemanticValidator là **Critic**, không chỉnh DBML.
5. LLM không quyết định PASS/FAIL cuối cùng.
6. `ValidationPolicy` bằng code quyết định `PASS`, `PASS_WITH_WARNINGS`, `FAIL`.
7. Mọi semantic ERROR phải có evidence cụ thể.
8. Validation result gắn với đúng revision/proposal snapshot.
9. Agent-generated model retry tối đa 3 lần khi còn ERROR.
10. Human Review vẫn là boundary cuối cùng cho proposal cần phê duyệt.
11. Rule catalog và `ValidationIssueCode` registry phải là source of truth duy nhất cho validation behavior.

---

# 20. Relationship With Existing Project Documents

Tài liệu này cụ thể hóa phần Validation đã được nhắc trong Master Requirements và Data Flow hiện tại.

Các nội dung hiện tại được giữ nguyên:

- Data Model phải được validation trước approval.
- Validation phải kiểm tra lỗi cấu trúc và Data Warehouse design.
- Requirement, Analytical Requirement và Source Data là context của Data Warehouse Design.
- Agent-generated invalid model được retry tối đa 3 lần.
- Human Review được giữ lại.
- Revision và Proposal lifecycle không bị thay đổi bởi validation architecture.

Các nội dung được thay đổi/bổ sung bởi tài liệu này:

- `ValidationEngine` đơn khối được thay bằng `ModelValidationService` gồm nhiều validator chuyên trách.
- Bổ sung `SemanticValidator` dùng LLM cho rule cần hiểu nghĩa.
- Bổ sung `ValidationAggregator` và deterministic `ValidationPolicy`.
- Chuẩn hóa `ValidationIssue`, severity, category, evidence và validator source.
- Mở rộng stable `ValidationIssueCode` registry.
- Định nghĩa đầy đủ rule catalog để implementation và test không tự suy diễn rule.

