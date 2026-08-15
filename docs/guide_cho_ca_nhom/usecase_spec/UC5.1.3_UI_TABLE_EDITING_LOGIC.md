# UC5.1.3 — Chỉnh sửa bảng trên giao diện

> **Mục tiêu:** Đặc tả chi tiết logic nghiệp vụ, luồng tương tác User–Frontend–Backend và các quy tắc UI/validation cho chức năng **chỉnh sửa bảng trên giao diện**, trong đó thao tác của User phải được phản ánh thành DBML và lưu vào Data Model hiện tại theo cơ chế revision/optimistic locking.

## 1. Căn cứ từ tài liệu dự án

UC5.1.3 được định nghĩa là:

> User sửa trực tiếp thông số, thêm cột,... trên giao diện → Mã DBML được cập nhật lại.

Chức năng nằm trong nhóm **UC5 — Quản lý Data Model / DDL**, cùng với:
- UC5.1.1 — Chỉnh sửa mã DBML thủ công.
- UC5.1.2 — Chỉnh sửa mã DBML bằng AI.
- UC5.2.1 — Xem ERD.
- UC5.2.2 — Chọn/di chuyển đối tượng trên ERD.
- UC5.3 — Xem nội dung phân tích.
- UC5.4 — Xem DDL.
- UC5.5 — Tải file SQL.

Tài liệu Data Model quy định Data Model hiện tại gồm `dbml`, `revision`, `created_at`, `updated_at`. Khi User chỉnh sửa:

```text
Get Current DBML + Revision
        ↓
      Edit
        ↓
Submit DBML + Base Revision
        ↓
Check Current Revision
        ↓
revision khớp?
   ┌────┴────┐
  YES        NO
   ↓          ↓
Update      Reject
DBML        Update
   ↓          ↓
Increase    Notify Conflict
Revision       ↓
   ↓        Reload / Review
 Commit
```

Các tài liệu cũng yêu cầu transaction + optimistic locking để tránh lost update.

---

# 2. Phạm vi của UC5.1.3

UC5.1.3 là **chỉnh sửa cấu trúc Data Model bằng form/UI trực quan**, không phải nhập DBML bằng text editor.

User cần có thể thao tác trên các thành phần của Data Model ở mức bảng và cột.

### 2.1. Các thao tác chính

User có thể:

1. Chọn một bảng.
2. Xem thông tin bảng.
3. Sửa thông tin bảng.
4. Thêm cột.
5. Sửa cột.
6. Xóa cột.
7. Thay đổi thuộc tính của cột.
8. Thêm bảng mới.
9. Xóa bảng.
10. Xem các thay đổi đang thực hiện trước khi lưu.
11. Hủy các thay đổi chưa lưu.
12. Lưu toàn bộ thay đổi thành một phiên bản Data Model mới.

> **Lưu ý:** Tài liệu hiện tại xác nhận rõ việc sửa thông số, thêm cột và cập nhật DBML, nhưng chưa đặc tả đầy đủ từng control UI. Những chi tiết UI dưới đây là **đề xuất triển khai cho MVP**, không phải requirement đã được phê duyệt.

---

# 3. Đề xuất bố cục giao diện

Để tránh User phải thao tác quá nhiều lần, nên thiết kế màn hình (màn hình khi user double click vào 1 bảng trên canvas) theo mô hình:

```text
┌─────────────────────────────────────────────────────────────┐
│ Data Model                            Revision: 3    [Save] │
├──────────────────┬──────────────────────────────────────────┤
│                  │                                          │
│ TABLE LIST       │ TABLE DETAIL                             │
│                  │                                          │
│ *users*          │ Table: users                             │
│ orders           │ Description / Note: ...                  │
│ products         │                                          │
│                  │ Columns                    [+ Add Column]│
│                  │                                          │
│                  │ id       uuid      PK   NN               │
│                  │ name     varchar   NN                    │
│                  │ price    decimal                         │
│                  │                                          │
│                  │ [Delete Table]                           │
│                  │                                          │
├──────────────────┴──────────────────────────────────────────┤
│ Unsaved changes: 3                         [Cancel] [Save]  │
└─────────────────────────────────────────────────────────────┘
```

## 3.1. Thành phần giao diện

### A. Table List

Hiển thị toàn bộ bảng trong DBML hiện tại.

Mỗi item tối thiểu hiển thị:
- Tên bảng.
- Trạng thái có thay đổi chưa lưu nếu có.

Thao tác:
- Click 1 lần → chọn bảng 
- Double Click → hiển thị modal chi tiết của các bảng (data model).
- Nút `+ Add Table` → mở form tạo bảng.
- Có thể có nút xóa trực tiếp hoặc đặt trong Table Detail.

### B. Table Detail

Hiển thị thông tin bảng đang được chọn.

Bao gồm:
- Tên bảng.
- Note/description nếu DBML hiện tại có thông tin này.
- Danh sách columns.
- Nút `Add Column`.
- Nút `Delete Table`.

### C. Column List

Mỗi column hiển thị dạng một row.

Ví dụ:

```text
Name        Type        PK     NN     Unique     Default     Action
id          uuid        ✓      ✓      -          -           Edit/Delete
name        varchar            ✓      -          -           Edit/Delete
email       varchar            ✓      -          -           Edit/Delete
```

Không nên bắt User mở modal riêng cho mọi thay đổi nhỏ nếu có thể chỉnh trực tiếp inline.

---

# 4. Luồng tương tác tổng thể

## 4.1. Bước 1 — Mở Data Model

User:

```text
Màn hình canvas
  ↓
Double click vào 1 bảng bất kỳ trên canvas
  ↓
Mở giao diện Data Model
  ↓
Hiển thị màn hình chỉnh sửa bảng
```

Frontend gọi Backend để lấy:

```text
data_model_id
project_id
dbml
revision
```

Frontend parse DBML thành model dữ liệu để render UI.

### Trạng thái ban đầu

```text
isEditting = false
baseRevision = current revision
```

Ví dụ:

```text
revision = 3
baseRevision = 3
```

---

# 5. Luồng sửa một bảng

## 5.1. Chọn bảng

User **click 2 lần** vào `orders`.

Frontend hiển thị:

```text
Table: orders

Columns:
- id
- customer_id
- order_date
- total_amount
```

Không gọi API chỉ để chọn bảng.

Đây là thao tác local trên Frontend.

---

## 5.2. Sửa tên bảng

User click vào tên bảng hoặc nút `Edit`.

UI cho phép sửa:

### Field: Table Name

- Kiểu: text input.
- Bắt buộc.
- Không được rỗng.
- Không được chỉ chứa whitespace.
- Phải là identifier hợp lệ theo cú pháp DBML.
- Không được trùng tên bảng khác trong cùng Data Model.
- Không được dùng tên không thể biểu diễn hợp lệ trong DBML.

Ví dụ:

```text
orders
```

→

```text
fact_orders
```

Sau khi User thay đổi:

```text
isEditting = true
```

**Chưa cập nhật DB ngay.**

---

# 6. Sửa thông tin bảng

Các field nên hỗ trợ:

| Field | Bắt buộc | Cho sửa | Ghi chú |
|---|---:|---:|---|
| Table Name | Có | Có | Identifier của bảng |
| Note / Description | Không | Có | Nếu mô hình sử dụng note |
| Columns | Có thể có | Có | Danh sách column |
| Relationships | Có | Theo quan hệ | Không nên sửa bằng text tự do |
| Indexes | TBD | TBD | Chỉ triển khai nếu requirement UI được xác nhận |

### Lưu ý

Tài liệu hiện tại xác nhận Data Model/DBML, nhưng **chưa quy định đầy đủ UI cho indexes, table notes, table settings hoặc relationship editor**.

Vì vậy:

- `Table Name` và `Columns`: nên đưa vào MVP của UC5.1.3.
- `Note/Description`: có thể hỗ trợ nếu DBML hiện tại chứa note.
- `Indexes`: đánh dấu `TBD` nếu chưa có requirement chi tiết.
- Relationship editor: nên tách rõ với UC5.2.2/ERD nếu chưa thống nhất UI.

---

# 7. Thêm bảng

User:

```text
Click [+ Add Table]
```

→ Mở form/modal.

## 7.1. Form Add Table

### Field 1 — Table Name

- Required.
- Không rỗng.
- Trim whitespace.
- Identifier hợp lệ.
- Không trùng table name hiện tại.

### Field 2 — Note

- Optional.
- Text.

### Field 3 — Columns

- Tạo bảng với danh sách column rỗng và yêu cầu User thêm column.

**Đề xuất MVP:** cho phép tạo bảng rồi thêm column ngay trong Table Detail.

## 7.2. Nút

```text
[Cancel] [Add Table]
```

Click `Add Table`:

- Validate.
- Nếu hợp lệ → thêm table vào local state.
- `isEditting = true`.
- Chưa gọi Backend.

---

# 8. Thêm cột

Đây là thao tác cốt lõi của UC5.1.3.

User:

```text
Chọn table
    ↓
Click [+ Add Column]
```

→ Hiển thị một row mới hoặc form inline.

## 8.1. Các field của Column

### 1. Column Name

**Bắt buộc**

Kiểu:

```text
text
```

Validation:

- Không rỗng.
- Trim whitespace.
- Identifier hợp lệ theo DBML.
- Không trùng column name trong cùng table.

Ví dụ:

```text
customer_id
```

---

### 2. Data Type

**Bắt buộc**

UI nên dùng dropdown/select thay vì để User nhập tùy ý trong MVP.

Ví dụ có thể hỗ trợ các type phổ biến:

```text
integer
bigint
smallint
decimal
numeric
float
double
boolean
varchar
text
date
timestamp
timestamp with time zone
uuid
json
jsonb
```

> Danh sách chính thức cần thống nhất với DBML parser/codegen của hệ thống. Không nên tự ý thêm type mà backend/codegen chưa hỗ trợ.

Nếu type có tham số:

```text
varchar(255)
decimal(18,2)
```

có thể hiển thị thêm field tương ứng.

---

### 3. Primary Key

Kiểu:

```text
checkbox
```

Cho phép đánh dấu column là PK.

Ví dụ:

```text
[x] Primary Key
```

Khi bật:

```text
id uuid [pk]
```

Nếu hệ thống hỗ trợ composite primary key, User có thể chọn nhiều column.

**Tuy nhiên:** DBML/database requirements hiện tại chưa đặc tả rõ UI cho composite key. Vì vậy implementation MVP cần xác nhận trước khi cho phép nhiều PK.
> Cho phép hỗ trợ composite primary key

---

### 4. Not Null

Kiểu:

```text
checkbox
```

Nếu bật:

```text
id uuid [not null]
```

---

### 5. Unique

Kiểu:

```text
checkbox
```

Nếu bật:

```text
email varchar [unique]
```

---

### 6. Default

Kiểu:

```text
text input
```

Ví dụ:

```text
0
```

hoặc:

```text
now()
```

Không nên tự động thêm quote nếu chưa xác định User nhập string hay SQL expression.

**Quan trọng:** Backend phải validate/parse giá trị default trước khi đưa vào DBML/DDL.

---

### 7. Note

Kiểu:

```text
text input / textarea
```

Ví dụ:

```text
Mã định danh bệnh nhân
```

DBML có thể biểu diễn thành note tùy syntax mà parser của hệ thống hỗ trợ.

---

### 8. Foreign Key

Nếu hệ thống cho phép sửa relationship trực tiếp tại Column Detail, cần có:

```text
Foreign Key: [None / Select]
```

Khi chọn:

```text
Referenced Table: departments
Referenced Column: id
```

DBML relationship tương ứng phải được tạo/cập nhật.

Tuy nhiên, tài liệu hiện tại chưa quy định chi tiết UI relationship editor cho UC5.1.3. Do đó phần này nên được đánh dấu **TBD hoặc tách sang UC5.2.2** nếu team đã thống nhất ERD là nơi quản lý relationship.

---

# 9. Sửa cột

User click trực tiếp vào row:

Có thể chỉnh:

```text
Column Name
Data Type
Primary Key
Not Null
Unique
Default
Note
Foreign Key (nếu được hỗ trợ)
```

Mọi thay đổi chỉ cập nhật **local editing state**.

Ví dụ:

```text
id
↓
user_id
```

Frontend cập nhật model:

```text
isDirty = true
```

Chưa gọi API.

---

# 10. Xóa cột

User:

```text
Click Delete Column
```

Không nên xóa ngay mà cần confirmation.

Dialog:

```text
Delete column?

Are you sure you want to delete column "customer_id"?

[Cancel] [Delete]
```

## Nếu User chọn Delete

Column bị xóa khỏi local model.

Nếu column đang tham gia relationship:

```text
customer_id → customers.id
```

thì hệ thống phải phát hiện dependency.

Không được âm thầm xóa relationship nếu chưa có rule rõ ràng.

Có thể hiển thị:

```text
This column is referenced by a relationship.
Deleting it will also affect the relationship.

[Cancel] [Continue]
```

Tuy nhiên, hành vi cascade cụ thể hiện chưa được tài liệu quy định → **TBD**.

---

# 11. Xóa bảng

User:

```text
Select table
↓
Delete Table
```

Hiển thị confirmation.

Ví dụ:

```text
Delete table "orders"?

This action will remove the table from the current model.

[Cancel] [Delete]
```

Nếu bảng có relationship:

```text
orders.customer_id → customers.id
```

phải cảnh báo dependency.

Không tự ý quyết định cascade nếu requirement chưa quy định.

---

# 12. Khi nào Frontend gọi Backend?

## Không gọi Backend cho từng lần click

Không nên:

```text
User sửa column
→ API
→ DB
```

cho từng field.

Điều này sẽ tạo quá nhiều request và khiến việc chỉnh sửa trở nên khó kiểm soát.

### Nên:

```text
Get Data Model
      ↓
Local Editing
      ↓
Multiple changes
      ↓
User clicks Save
      ↓
Submit complete DBML + base_revision
      ↓
Backend validates revision
      ↓
Update DBML
      ↓
revision + 1
```

Đây cũng phù hợp trực tiếp với lifecycle User Editing trong requirements.

---

# 13. Nút Save

Nút Save nên xuất hiện ở header hoặc footer cố định.

Trạng thái:

### Không có thay đổi

```text
[Save] disabled
```

### Có thay đổi

```text
[Save] enabled
```

Khi User click Save:

```text
1 click
```

Frontend gửi:

```text
data_model_id
dbml
base_revision
```

Trong đó:

```text
base_revision = revision tại thời điểm User mở Data Model
```

---

# 14. Backend xử lý Save

Backend phải kiểm tra:

```text
Current revision == base_revision ?
```

## Case A — Revision khớp

Ví dụ:

```text
Frontend base_revision = 3
DB current revision = 3
```

→ Cho phép update.

Transaction:

```text
BEGIN

UPDATE data_models
SET
    dbml = new_dbml,
    revision = revision + 1,
    updated_at = ...

COMMIT
```

Kết quả:

```text
revision 3 → 4
```

Frontend nhận Data Model mới.

UI:

```text
Saved successfully
Revision: 4
```

`isDirty = false`.

---

# 15. Case B — Revision conflict

Ví dụ:

```text
Frontend base_revision = 3
DB current revision = 4
```

Điều này có nghĩa Data Model đã bị User/Proposal khác cập nhật trong lúc User đang chỉnh sửa.

Backend:

```text
Reject Update
```

Không được overwrite DBML hiện tại.

Frontend hiển thị:

```text
Data Model has been changed by another update.

Your changes were based on revision 3,
but the current revision is 4.

Please reload the latest version and review your changes before saving again.

[Reload Latest]
```

Theo requirements, hệ thống phải yêu cầu User **Reload / Review**, không tự động merge.

---

# 16. Conflict UX

Khi conflict xảy ra, **không nên tự động mất toàn bộ nội dung User vừa chỉnh**.

Frontend nên giữ:

```text
Local edited model
```

và đồng thời lấy:

```text
Latest server model
```

Sau đó có thể cho User lựa chọn:

```text
[Reload Latest]
[Review Changes]
```

### MVP tối thiểu

```text
Conflict detected.

[Discard My Changes & Reload]
```

### Nếu muốn UX tốt hơn

Hiển thị:

```text
Your version          Latest version
Revision 3            Revision 4
------------------------------------------------
orders                 orders
customer_id            customer_id
total                   total
status                  order_status
```

Nhưng chức năng diff/merge chi tiết **chưa được requirement hiện tại xác nhận**, nên có thể để TBD.

---

# 17. Validation trước Save

Validation nên có hai lớp.

## 17.1. Frontend validation

Kiểm tra nhanh:

### Table

- Table name không rỗng.
- Table name hợp lệ.
- Table name không trùng.

### Column

- Column name không rỗng.
- Column name hợp lệ.
- Column name không trùng trong table.
- Data type hợp lệ.
- Default có format hợp lệ nếu có.
- Các thuộc tính không mâu thuẫn.

Ví dụ:

```text
Column name: empty
→ Error ngay dưới field
```

---

## 17.2. Backend validation

Backend không được tin dữ liệu Frontend.

Backend phải:

1. Validate request.
2. Parse/validate DBML.
3. Kiểm tra tính hợp lệ của Data Model.
4. Kiểm tra revision.
5. Update bằng transaction + optimistic locking.

Không được chỉ dựa vào validation của Frontend.

---

# 18. DBML được cập nhật như thế nào?

Frontend nên duy trì một structured model thay vì thao tác string DBML trực tiếp.

Ví dụ local model:

```text
DataModel
 ├── tables
 │    ├── Table
 │    │    ├── name
 │    │    ├── note
 │    │    └── columns
 │    │         ├── name
 │    │         ├── type
 │    │         ├── pk
 │    │         ├── notNull
 │    │         ├── unique
 │    │         ├── default
 │    │         └── note
 │    └── ...
 └── relationships
```

Khi User chỉnh sửa:

```text
UI Model
   ↓
DBML Serializer
   ↓
DBML
```

Khi load:

```text
DBML
   ↓
DBML Parser
   ↓
UI Model
```

Như vậy UI không phải thao tác chuỗi DBML bằng các phép replace string thủ công.

---

# 19. Khi User đang chỉnh sửa nhưng Agent tạo Proposal

Đây là một trường hợp quan trọng.

Ví dụ:

```text
User mở revision 3
↓
User đang chỉnh sửa
↓
Agent tạo proposal dựa trên revision 3
```

Proposal không được tự động ghi đè Data Model hiện tại.

Nếu User lưu trước:

```text
revision 3 → revision 4
```

thì proposal của Agent vẫn có:

```text
base_revision = 3
```

Khi Apply proposal:

```text
3 != 4
```

→ Proposal phải trở thành `CONFLICTED`.

Điều này phù hợp với quy tắc Data Model Protection và Optimistic Locking.

---

# 20. Quan hệ với UC5.1.1 và UC5.1.2

Ba chức năng cùng thay đổi một Data Model nhưng khác cách nhập:

| Use Case | Cách chỉnh sửa | Kết quả |
|---|---|---|
| UC5.1.1 | Gõ DBML trực tiếp | DBML mới |
| UC5.1.2 | Natural language → AI | Proposal/DBML theo workflow AI |
| UC5.1.3 | Form/UI trực quan | DBML mới |

Điểm quan trọng:

**Không tạo ba cơ chế lưu Data Model hoàn toàn khác nhau.**

Nên có một application/domain flow chung:

```text
UI / DBML Editor / AI Proposal
              ↓
        Data Model Update
              ↓
       Validate Revision
              ↓
       Optimistic Locking
              ↓
        Save Data Model
```

Riêng AI Proposal vẫn tuân thủ Human Review và `data_model_changes`.

---

# 21. Các trường UI nên có trong MVP

## Table

| Field | UI | Required | Validation |
|---|---|---:|---|
| Table Name | Text input | YES | Identifier, unique |
| Note | Textarea | NO | Text |

## Column

| Field | UI | Required | Validation |
|---|---|---:|---|
| Column Name | Text input | YES | Identifier, unique trong table |
| Data Type | Select | YES | Type được parser hỗ trợ |
| Primary Key | Checkbox | NO | Theo PK rule |
| Not Null | Checkbox | NO | DBML constraint |
| Unique | Checkbox | NO | DBML constraint |
| Default | Text input | NO | Default hợp lệ |
| Note | Textarea | NO | Text |
| Foreign Key | Select/Relationship editor | TBD | Chưa đủ UI requirement |

---

# 22. Trải nghiệm thao tác đề xuất

## Kịch bản 1 — Sửa một column

```text
1. User mở Data Model
2. User click table
3. User click column
4. User sửa field
5. UI cập nhật local state
6. User click Save
7. Backend kiểm tra revision
8. Backend validate DBML
9. Backend update DBML
10. revision tăng
11. Frontend hiển thị thành công
```

**Tổng số click tối thiểu:** phụ thuộc số field cần sửa; chỉ có **1 lần Save** cho toàn bộ batch thay đổi.

---

## Kịch bản 2 — Thêm column

```text
1. User click table
2. User click Add Column
3. Nhập Column Name
4. Chọn Data Type
5. Chọn constraints nếu cần
6. Click Add/Done
7. UI thêm column
8. User click Save
```

---

## Kịch bản 3 — Thêm nhiều column

Không nên bắt User:

```text
Add Column
Save
Add Column
Save
Add Column
Save
```

Nên:

```text
Add Column
Add Column
Add Column
...
Save một lần
```

---

## Kịch bản 4 — Sửa nhiều bảng

Cho phép:

```text
Table A
  sửa 2 columns

Table B
  thêm 1 column

Table C
  đổi tên
      ↓
Save một lần
```

Tất cả thay đổi tạo thành **một DBML snapshot mới** và một lần kiểm tra revision.

---

# 23. Trạng thái UI

Frontend nên có tối thiểu:

```text
LOADING
READY
EDITING
SAVING
SAVED
VALIDATION_ERROR
CONFLICT
ERROR
```

### LOADING

Đang lấy Data Model.

### READY

Đã tải thành công, chưa thay đổi.

### EDITING

Có thay đổi local.

### SAVING

Đang gửi Save request.

Không cho gửi nhiều Save request đồng thời.

### SAVED

Lưu thành công.

### VALIDATION_ERROR

DBML không hợp lệ.

Hiển thị lỗi đủ để User biết cần sửa gì.

### CONFLICT

Revision đã thay đổi.

### ERROR

Lỗi hệ thống/API.

---

# 24. Những gì KHÔNG nên làm

## Không 1 — Auto-save từng field

Không nên:

```text
User đổi type
→ API
→ DB
```

vì gây nhiều request và khó kiểm soát revision.

## Không 2 — Frontend tự tăng revision

Frontend không được:

```text
revision++
```

Revision phải do Backend/Database quản lý.

## Không 3 — Ghi đè khi revision conflict

Không được:

```text
current revision = 4
frontend base = 3

→ overwrite DBML
```

Đây là lost update.

## Không 4 — Tự động merge conflict trong MVP

Requirements xác định không tự động merge Proposal cũ với Data Model mới vì có thể làm mất thay đổi của User.

## Không 5 — Backend tin DBML từ Frontend

DBML phải được validate lại ở Backend.

## Không 6 — Để UI tự quyết định business rule

Frontend chỉ hỗ trợ interaction và validation trải nghiệm.

Business validation phải nằm ở Application/Domain/Backend theo Clean Architecture.

---

# 25. API contract ở mức logic

Tài liệu hiện tại chưa cung cấp API Reference chi tiết, vì vậy phần này là **đề xuất contract cho implementation**, không phải API đã được approved.

### GET current Data Model

```text
GET /projects/{project_id}/data-model
```

Response logic (Phần dữ liệu trường data trong api response chung): 

```json
{
  "id": "...",
  "project_id": "...",
  "dbml": "...",
  "revision": 3
}
```

### Update Data Model

```text
PUT /projects/{project_id}/data-model
```

Request logic:

```json
{
  "data_model_id": "...",
  "dbml": "...",
  "base_revision": 3
}
```

Success:

```text
200 OK
revision = 4
```

Conflict:

```text
Business error:
DATA_MODEL_REVISION_CONFLICT
```

> Tên endpoint, HTTP method, response envelope và ErrorCode chính thức cần đối chiếu với API specification hiện tại trước khi code.

---

# 26. Backend/Clean Architecture mapping

Theo Coding Guidelines:

```text
Presentation
    ↓
Application Use Case
    ↓
Domain
    ^
    |
Infrastructure
```

Không đặt business logic vào FastAPI Router.

Có thể tổ chức logic:

```text
Presentation
└── Data Model Controller / Router

Application
└── UpdateDataModelService
    ├── Get current Data Model
    ├── Validate request
    ├── Validate revision
    └── Update Data Model

Domain
└── DataModel
    ├── dbml
    └── revision

Infrastructure
└── DataModelRepository
```

Repository chịu trách nhiệm persistence.

Optimistic locking phải được đảm bảo ở tầng persistence/transaction phù hợp.

---

# 27. Error cases cần test

## Input

- Table name rỗng.
- Column name rỗng.
- Column trùng tên.
- Table trùng tên.
- Data type không hợp lệ.
- DBML malformed.
- Default không hợp lệ.

## Business

- Data Model không tồn tại.
- User không có quyền truy cập Project.
- User không có quyền chỉnh sửa Data Model.
- Project không tồn tại.
- Data Model ở trạng thái không cho phép chỉnh sửa nếu sau này có rule này.

## Concurrency

- User A mở revision 3.
- User B mở revision 3.
- User A Save → revision 4.
- User B Save với base revision 3.
- B phải nhận conflict.

## Agent concurrency

- Agent proposal base revision 3.
- User update Data Model → revision 4.
- User Accept proposal.
- Proposal phải trở thành `CONFLICTED`, không overwrite revision 4.

---

# 28. Acceptance Criteria cho UC5.1.3

### AC-01 — Load

- [ ] User có thể mở Data Model hiện tại.
- [ ] UI nhận được DBML và revision hiện tại.
- [ ] UI render được danh sách table/column.

### AC-02 — Table

- [ ] User có thể thêm table.
- [ ] User có thể sửa table name.
- [ ] User có thể xóa table.
- [ ] Hệ thống validate table name.

### AC-03 — Column

- [ ] User có thể thêm column.
- [ ] User có thể sửa column.
- [ ] User có thể xóa column.
- [ ] User có thể sửa column name.
- [ ] User có thể sửa data type.
- [ ] User có thể cấu hình PK.
- [ ] User có thể cấu hình NOT NULL.
- [ ] User có thể cấu hình UNIQUE.
- [ ] User có thể cấu hình DEFAULT.
- [ ] User có thể cấu hình NOTE nếu parser hỗ trợ.

### AC-04 — DBML

- [ ] Mọi thay đổi UI được phản ánh vào DBML local.
- [ ] DBML được validate trước khi lưu.
- [ ] DBML lưu thành công trở thành Data Model hiện tại.

### AC-05 — Revision

- [ ] Save gửi `base_revision`.
- [ ] Backend kiểm tra revision.
- [ ] Revision khớp → update thành công.
- [ ] Revision tăng đúng 1.
- [ ] Revision không khớp → không overwrite.
- [ ] Conflict được thông báo cho User.

### AC-06 — Concurrency

- [ ] Concurrent update không gây lost update.
- [ ] Transaction + optimistic locking được sử dụng.
- [ ] Proposal cũ không được ghi đè Data Model mới.

### AC-07 — UX

- [ ] User có thể chỉnh nhiều thay đổi trước khi Save.
- [ ] Save chỉ thực hiện khi có thay đổi.
- [ ] Trong khi Save đang chạy không cho gửi duplicate request.
- [ ] Có loading state.
- [ ] Có success state.
- [ ] Có validation error.
- [ ] Có conflict state.

---

# 29. Các điểm cần xác nhận trước khi code

Tài liệu hiện tại chưa đặc tả đầy đủ các điểm sau. Theo nguyên tắc của Master Requirements, không nên tự biến các điểm này thành business rule chính thức.

### TBD-01 — Có cho phép sửa Relationship trực tiếp trong UC5.1.3 không?

Có thể:
- Chỉ sửa table/column ở UC5.1.3.
- Relationship được chỉnh qua ERD/UC5.2.2.

### TBD-02 — Có cho phép Composite Primary Key không?

DBML có thể biểu diễn nhưng UI requirement hiện tại chưa xác định.

### TBD-03 — Danh sách Data Type chính thức

Cần thống nhất với:
- DBML parser.
- DBML validator.
- SQL codegen.
- Sandbox DB.

### TBD-04 — Index editor

Database model có index nhưng UC5.1.3 chưa quy định UI chỉnh index.

### TBD-05 — Table Note

Cần xác nhận có coi note/description là field chính thức của Table Editor hay không.

### TBD-06 — Conflict Diff UI

Requirements bắt buộc xử lý conflict nhưng chưa yêu cầu một màn hình merge/diff hoàn chỉnh.

MVP có thể chỉ:

```text
Conflict
↓
Reload latest
↓
User review
↓
Edit lại
↓
Save
```

### TBD-07 — Auto-save

Requirements mô tả flow `Edit → Submit DBML`, không yêu cầu auto-save.

Đề xuất MVP: **không auto-save**.

---

# 30. Luồng hoàn chỉnh cuối cùng

```text
                 USER
                   │
                   ▼
          Open Data Model
                   │
                   ▼
        GET DBML + Revision
                   │
                   ▼
             FRONTEND
                   │
          Parse DBML → UI Model
                   │
                   ▼
              User edits
                   │
       ┌───────────┼───────────┐
       │           │           │
   Edit Table   Add Column   Delete Column
       │           │           │
       └───────────┼───────────┘
                   │
                   ▼
             Local Model
                   │
              isDirty=true
                   │
                   ▼
              User clicks Save
                   │
                   ▼
          Serialize → DBML
                   │
                   ▼
              BACKEND
                   │
          Validate DBML
                   │
          Check Base Revision
                   │
             ┌─────┴─────┐
             │           │
          MATCH       CONFLICT
             │           │
             ▼           ▼
       Transaction     Reject
             │           │
       Update DBML      │
             │           ▼
       revision + 1   Notify User
             │           │
             ▼           ▼
           COMMIT    Reload / Review
             │
             ▼
          FRONTEND
             │
       Revision = N+1
             │
       isDirty = false
             │
             ▼
       Data Model updated
```

---

# 31. Kết luận cho MVP

Cách triển khai phù hợp nhất cho UC5.1.3 là:

> **UI chỉnh sửa một structured Data Model ở local state → User thực hiện nhiều thay đổi → Serialize thành DBML → Submit một lần → Backend validate DBML + kiểm tra base revision → optimistic locking/transaction → cập nhật Data Model và tăng revision.**

Không nên lưu DB sau từng thao tác UI.

Điểm quan trọng nhất của chức năng không chỉ là “thêm/sửa/xóa cột”, mà là phải bảo đảm:

```text
UI Model
   ↕
DBML
   ↓
Validation
   ↓
Revision Check
   ↓
Optimistic Locking
   ↓
Official Data Model
```

Đây là cách giữ UC5.1.3 nhất quán với UC5.1.1, UC5.1.2, Human-in-the-Loop và Data Model Lifecycle hiện tại.
