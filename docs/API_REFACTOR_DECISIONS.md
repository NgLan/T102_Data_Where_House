# API Refactor Decisions

## 1. Mục tiêu

Tài liệu này chốt lại các thay đổi API sau khi review `openapi.json`, `usecase.md`, `database.md` và `data_flow.md`.

Nguyên tắc chính:

- Tên endpoint phải phản ánh đúng hành động của người dùng và business semantics.
- Không giữ proposal/Human Review ở những luồng mà người dùng đã chủ động yêu cầu ghi đè Data Model hiện tại.
- DDL được sinh từ Data Model nên thuộc resource Data Model, không thuộc Sandbox.
- Frontend đọc tài liệu Requirement (`DOCX`, `TXT`, `MD`) thành raw text; Backend chỉ parse/profile Data Source CSV và chịu trách nhiệm DBML generation, DDL codegen, validation, authorization và persistence.

---

## 2. Luồng Analysis

### 2.1. GET `/analysis-status`

```http
GET /api/v1/projects/{project_id}/analysis-status
```

Mục đích:

- Chỉ đọc trạng thái đồng bộ/outdate của các kết quả downstream.
- Không gọi LLM/Agent.
- Dùng để Frontend quyết định có cần hiển thị `Analyze Changes`, `Update Data Model` hoặc không cần action nào.

Response có thể tiếp tục gồm:

```text
requirement_analysis_outdated
source_analysis_outdated
data_model_outdated
data_model_exists
recommended_action
```

Description đề xuất:

> Trả về trạng thái outdate của Requirement Analysis, Source Analysis và Data Model để Frontend xác định hành động tiếp theo. Endpoint không chạy Agent.

### 2.2. POST `/reanalyze`

```http
POST /api/v1/projects/{project_id}/reanalyze
```

Mục đích:

- Chạy lại các bước Requirement Analysis / Analytical Requirement Analysis cần thiết dựa trên Requirement và SchemaMetadata hiện tại.
- Không tự cập nhật Data Model.
- Dùng cho action `Analyze Changes`.

Description đề xuất:

> Phân tích lại các kết quả đã outdate từ Requirement và SchemaMetadata hiện tại. Cập nhật Requirements/Analytical Requirements nhưng không thay đổi Data Model.

---

## 3. Update Data Model không tạo Proposal

### 3.1. Semantics đã chốt

Khi User bấm `Update Data Model`, User đã chủ động yêu cầu hệ thống tạo lại Data Model theo Requirement/Source hiện tại.

Do đó luồng phải là:

```text
Requirements hiện tại
+
Analytical Requirements hiện tại
+
SchemaMetadata hiện tại
      ↓
DWDesignAgent
      ↓
Validation Engine
      ↓
DBML mới hợp lệ
      ↓
Ghi đè data_models.dbml
      ↓
revision = revision + 1
```

Không tạo `data_model_changes` cho luồng này.

Không dùng Human Review proposal cho action `Update Data Model`.

### 3.2. API đã chốt

```http
POST /api/v1/projects/{project_id}/data-model/regenerate
```

Mục đích:

- Sinh lại DBML từ input/analysis hiện tại.
- Validate DBML.
- Nếu thành công thì cập nhật trực tiếp Data Model hiện tại và tăng revision.
- Nếu Data Model chưa tồn tại, không dùng endpoint này; dùng `generate` cho lần đầu.

Description đề xuất:

> Sinh lại Data Model từ Requirement, Analytical Requirement và SchemaMetadata hiện tại; sau khi validation thành công, ghi đè snapshot DBML hiện tại và tăng revision.

### 3.3. Phân biệt `generate` và `regenerate`

```http
POST /api/v1/projects/{project_id}/data-model/generate
```

- Chỉ tạo Data Model lần đầu.
- Conflict nếu Project đã có Data Model.

```http
POST /api/v1/projects/{project_id}/data-model/regenerate
```

- Dùng khi Project đã có Data Model.
- Tạo lại DBML từ input/analysis hiện tại.
- Ghi đè Data Model hiện tại sau validation.
- Tăng revision.

---

## 4. AI chỉnh sửa Data Model vẫn dùng Proposal

Giữ luồng Human Review cho use case User nhập instruction bằng ngôn ngữ tự nhiên để AI chỉnh Data Model.

Endpoint đã chốt:

```http
POST /api/v1/projects/{project_id}/data-model/proposals/ai-edit
```

Request:

```json
{
  "instruction": "Tách DimDoctor thành DimDoctor và DimDepartment"
}
```

Luồng:

```text
Current DBML
+
User instruction
+
Project context
      ↓
DWDesignAgent
      ↓
Validation Engine
      ↓
data_model_changes
status = PROPOSED
base_revision = current revision
```

Sau đó User:

```http
POST /api/v1/data-model-changes/{change_id}/accept
POST /api/v1/data-model-changes/{change_id}/reject
```

Proposal được giữ vì đây là AI-proposed edit cần Human Review.

---

## 6. Refactor Data Source response

### 6.1. Bỏ các field

Bỏ khỏi `UploadDataSourcesResponse`:

```text
extracted_requirement_text
```

Bỏ khỏi column response/model:

```text
semantic_type
sample_values
options
```

Đồng bộ xóa `options` khỏi tất cả DTO liên quan, bao gồm request chỉnh sửa column.

### 6.2. `data_type`

`data_type` là kiểu dữ liệu hiển thị cho User, không nhất thiết là physical DB type.

Các giá trị có thể gồm:

```text
TEXT
CATEGORY
INTEGER
NUMBER
DECIMAL
DATE
TIME
DATETIME
BOOLEAN
```

Nếu một cột được xác định là category:

```json
{
  "name": "gender",
  "data_type": "CATEGORY",
  "distinct_count": 3,
  "distinct_values": ["Male", "Female", "Other"]
}
```

`distinct_values` chủ yếu có ý nghĩa với `CATEGORY` hoặc tập giá trị nhỏ phù hợp để hiển thị.

### 6.3. Thêm `constraints`

Mỗi column có thể trả thêm:

```json
{
  "constraints": [
    {
      "type": "FOREIGN_KEY",
      "reference_table": "departments",
      "reference_column": "department_id"
    }
  ]
}
```

Discriminated union của constraint gồm chính xác:

```text
FOREIGN_KEY
UNIQUE
CHECK
DEFAULT
```

- `FOREIGN_KEY`: `type`, `reference_table`, `reference_column`.
- `UNIQUE`: chỉ có `type`.
- `CHECK`: `type`, `expression`.
- `DEFAULT`: `type`, `value`; `value` là `string | number | boolean | null`.

Mỗi phần tử phải khớp đúng một nhánh theo `type`; không nhận string constraint hay field legacy.

`primary_key` và `nullable` vẫn giữ thành field riêng vì UI sử dụng thường xuyên.

Không tự biến observed statistics thành business/database constraint.

Ví dụ:

```text
observed min(age) = 18
observed max(age) = 92
```

không được tự suy ra:

```sql
CHECK age BETWEEN 18 AND 92
```

nếu source không cung cấp constraint chính thức hoặc User chưa xác nhận.

### 6.4. Response upload đề xuất

```json
{
  "status": "success",
  "code": 201,
  "message": "Xử lý thành công",
  "data": {
    "data_sources": [
      {
        "id": "uuid",
        "project_id": "uuid",
        "name": "patients.csv",
        "type": "CSV",
        "description": null,
        "tables": [
          {
            "name": "patients",
            "columns": [
              {
                "name": "gender",
                "data_type": "CATEGORY",
                "nullable": true,
                "primary_key": false,
                "null_count": 2,
                "distinct_count": 3,
                "distinct_values": ["Male", "Female", "Other"],
                "constraints": []
              }
            ]
          }
        ]
      }
    ],
    "total_files_processed": 1
  }
}
```

---

## 7. API chỉnh sửa Column

Không đổi thành:

```http
PATCH /api/v1/projects/{project_id}/data-sources/{data_source_id}
```

vì endpoint đó sẽ được hiểu là chỉnh chính Data Source, không phải một column bên trong metadata.

Endpoint đã chốt:

```http
PATCH /api/v1/projects/{project_id}/data-sources/{data_source_id}/tables/{table_name}/columns/{column_name}
```

Body chỉ chứa phần cần thay đổi, ví dụ:

```json
{
  "data_type": "CATEGORY",
  "distinct_values": ["Male", "Female", "Other"],
  "constraints": []
}
```

Dùng `PATCH` vì đây là partial update của metadata column.

---

## 8. Sandbox test connection

URL đã chốt:

```http
POST /api/v1/projects/{project_id}/sandbox/test-connection
```

vì Sandbox thuộc Project.

---

## 9. DDL code generation

DDL phải được sinh ở Backend.

Không sinh DDL ở Frontend.

Lý do:

- Một source of truth cho code generation.
- Hỗ trợ nhiều target DB thống nhất.
- Sandbox cũng cần cùng DDL generator.
- Frontend không phải maintain parser/generator riêng.

Endpoint đã chốt:

```http
GET /api/v1/projects/{project_id}/data-model/ddl?db_type=POSTGRESQL
```

DDL là output của Data Model, không phải resource của Sandbox.

Response giữ dạng:

```json
{
  "ddl": "...",
  "db_type": "POSTGRESQL",
  "data_model_revision": 5
}
```

Endpoint này được dùng cho:

```text
View DDL
Download SQL
Execute in Sandbox
```

Sandbox chỉ consume DDL.

---

## 10. Danh sách API sau khi chốt

| Chức năng                                                         | API                                                                             |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| Xem trạng thái outdate                                            | `GET /projects/{id}/analysis-status`                                            |
| Phân tích lại input đã thay đổi                                   | `POST /projects/{id}/reanalyze`                                                 |
| Lấy Data Model hiện tại                                           | `GET /projects/{id}/data-model`                                                 |
| User lưu DBML chỉnh thủ công                                      | `PUT /projects/{id}/data-model`                                                 |
| Sinh Data Model lần đầu                                           | `POST /projects/{id}/data-model/generate`                                       |
| Tạo lại Data Model từ input/analysis mới và ghi đè model hiện tại | `POST /projects/{id}/data-model/regenerate`                                     |
| User yêu cầu AI chỉnh model và tạo proposal                       | `POST /projects/{id}/data-model/proposals/ai-edit`                              |
| Xem proposal                                                      | `GET /projects/{id}/data-model-changes/{change_id}`                             |
| Accept proposal                                                   | `POST /data-model-changes/{change_id}/accept`                                   |
| Reject proposal                                                   | `POST /data-model-changes/{change_id}/reject`                                   |
| Upload Data Source CSV                                            | `POST /projects/{id}/data-sources/upload`                                       |
| Xem preview Data Source                                           | `GET /projects/{id}/data-sources/{source_id}/preview`                           |
| Sửa metadata một column                                           | `PATCH /projects/{id}/data-sources/{source_id}/tables/{table}/columns/{column}` |
| Xóa Data Source                                                   | `DELETE /projects/{id}/data-sources/{source_id}`                                |
| Lấy Sandbox config                                                | `GET /projects/{id}/sandbox/config`                                             |
| Lưu Sandbox config                                                | `POST /projects/{id}/sandbox/config`                                            |
| Test draft Sandbox config                                         | `POST /projects/{id}/sandbox/test-connection`                                   |
| Sinh DDL từ Data Model                                            | `GET /projects/{id}/data-model/ddl?db_type=...`                                 |
| Chạy DDL trên Sandbox                                             | `POST /projects/{id}/sandbox/execute-ddl`                                       |

---

## 11. Yêu cầu khi sửa code/OpenAPI

Codex cần cập nhật đồng bộ:

1. FastAPI routes và `operation_id`.
2. Application service interface/implementation.
3. Request/response DTO.
4. Domain/application output nếu contract thay đổi.
5. OpenAPI descriptions để mô tả đúng semantics mới.
6. Xóa endpoint/schema/field không còn sử dụng.
7. Cập nhật tests liên quan.
8. Export lại FastAPI OpenAPI.
9. Chạy lại generated Frontend API client/types; không sửa generated code thủ công.
10. Kiểm tra route, schema và field đã loại bỏ không còn trong source, OpenAPI hoặc generated client; SQL migration là ngoại lệ duy nhất được phép đọc các khóa metadata cũ.

## 12. Business rule quan trọng cần giữ

- Manual DBML update (`PUT /data-model`) vẫn dùng `base_revision` để optimistic locking.
- AI edit proposal vẫn lưu `base_revision`; Accept chỉ thành công nếu revision hiện tại còn khớp.
- `regenerate` là explicit User action nên được phép thay Data Model hiện tại sau khi generation + validation thành công.
- `reanalyze` không được tự động thay đổi Data Model.

## 13. Requirement document processing

- Backend không cung cấp API upload Requirement document.
- Frontend đọc `DOCX` bằng Mammoth `extractRawText({ arrayBuffer })` và đọc `TXT`/`MD` bằng `File.text()`.
- Raw text được điền vào Requirement editor và lưu qua Project API hiện có.
- CSV vẫn được gửi riêng tới Data Source upload API; tài liệu Requirement không được gửi tới Data Source API.
