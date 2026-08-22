Hãy kiểm tra implementation hiện tại của **trang Project Detail / Project Init** ở Frontend và các API/logic liên quan ở Backend, sau đó refactor theo các yêu cầu dưới đây. Phải tuân thủ architecture, coding guidelines, OpenAPI generated client và i18n hiện tại; không hardcode API DTO ở Frontend.

## 1. Header của Project Detail

- Thêm header cố định/phù hợp với layout hiện tại.
- Logo trên header phải clickable.
- Click Logo phải điều hướng về trang danh sách Projects.
- Trên header phải có Project Selector dạng Select/Dropdown.
- Selector hiển thị danh sách Project mà User có quyền truy cập.
- Khi chọn Project khác, điều hướng trực tiếp sang Project Detail của Project tương ứng.
- Project hiện tại phải được hiển thị là selected value.
- Không fetch lại danh sách Projects riêng ở nhiều component nếu đã có query/cache dùng chung phù hợp.

## 2. Raw Requirement và Requirements

Phải phân biệt rõ:

- `Raw Requirement` = `projects.requirement`, do User nhập và được phép chỉnh sửa.
- `Requirements` = kết quả đã được RequirementAgent phân tích thành `BUSINESS`, `ANALYTICAL`, `TECHNICAL`; chỉ được xem, không được chỉnh sửa trực tiếp.

### Raw Requirement

- Cho phép User chỉnh sửa Raw Requirement.
- Không cho phép chỉnh sửa trực tiếp từng Structured Requirement.

### Requirements Table

Hiển thị Requirements thành bảng gồm đúng 3 cột:

1. **Requirement**
   - Hiển thị `title`.
   - Hiển thị `description` bên dưới title.

2. **Type**
   - BUSINESS
   - ANALYTICAL
   - TECHNICAL

3. **Priority**
   - HIGH
   - MEDIUM
   - LOW

Cho phép click tiêu đề từng cột để sort.

Default sorting:

```text
Priority:
HIGH → MEDIUM → LOW

Nếu cùng Priority:
BUSINESS → ANALYTICAL → TECHNICAL

Nếu vẫn giống nhau:
Title A → Z
```

Khi sort cột Requirement thì sort theo `title`, không sort theo `description`.

Nếu API hiện tại vẫn cho User tạo/chỉnh Structured Requirement trực tiếp thì phải rà soát lại contract để phù hợp business rule mới: Structured Requirements chỉ là kết quả phân tích của RequirementAgent và không editable từ màn hình này.

## 3. Upload Data Source

Khu vực upload CSV phải thay đổi thành một **dropzone/clickable area lớn**.

- Không chỉ nút nhỏ `"Chọn dữ liệu nguồn"` mới clickable.
- Click vào bất kỳ vị trí phù hợp nào trong toàn bộ upload area đều mở file picker.
- Hỗ trợ drag & drop nếu implementation hiện tại đã có hoặc có thể bổ sung đơn giản.
- Giữ giới hạn tối đa 20 file theo requirement hiện tại.
- Chỉ hỗ trợ CSV trong MVP.
- Sau khi chọn file, file được đưa vào danh sách Data Source hiện tại.

## 4. Danh sách CSV

Hiển thị các CSV theo chiều dọc dạng collapsible list.

Mỗi file có hai trạng thái:

### Collapsed

Chỉ hiển thị:

- icon (Tùy vào file type, ví dụ CSV icon);
- tên file;
- nút/mũi tên mở;
- nút xóa.

Toàn bộ phần header theo chiều ngang của file phải clickable để mở file, không bắt User phải click chính xác vào icon.

Nút xóa phải hoạt động độc lập và không trigger expand/collapse.

### Expanded

Hiển thị metadata column dưới dạng bảng.

Bảng gồm:

1. **Column**
2. **Data Type**
3. **Properties**

Không dùng tên `"Constraint"` nếu dữ liệu thực tế chỉ là thông tin suy luận từ CSV.

`Properties` có thể hiển thị những thông tin thực sự có căn cứ như:

- Nullable
- Unique candidate
- Key candidate
- category values
- các property/profile khác đang tồn tại và có ý nghĩa

Không được biến statistics được quan sát từ CSV thành database constraint chính thức.

Nếu column có:

```text
data_type = CATEGORY
```

thì hiển thị category values trong cột `Properties`, phân cách bằng:

```text
,
```

Ví dụ:

```text
Nam, Nữ, Khác
```

## 5. Refactor Data Type Inference

Hiện tại CSV type inference đang cho nhiều kết quả sai, ví dụ:

```text
Column: Số hồ sơ
Values:
15020001
15020002
15020003

Current:
INTEGER

Expected logical type:
TEXT
```

Vì đây là identifier/code, không phải numeric measure.

Ví dụ khác:

```text
Column: Ghi chú

Current:
CATEGORY

Expected:
TEXT
```

Không được suy luận CATEGORY chỉ vì số lượng distinct value thấp.

Ví dụ khác:

```text
Column chứa ngày/tháng

Current:
TEXT

Expected:
DATE hoặc DATETIME
```

Phải hỗ trợ nhiều date/datetime format thường gặp thay vì chỉ dựa vào auto inference mặc định của DuckDB.

### Kiến trúc inference mới

Không bỏ DuckDB.

Sử dụng flow:

```text
CSV
↓
DuckDB parsing / initial type inference
↓
Data Profiler
↓
Rule-based logical type inference
↓
LLM ColumnTypeClassifier đối với column ambiguous / confidence thấp
↓
Final data_type
↓
SchemaMetadata
```

`DuckDB inferred type` chỉ là candidate ban đầu, không phải `data_type` cuối cùng của hệ thống.

## 6. Logical Data Type

Không thêm `semantic_type`.

Hệ thống chỉ dùng **một `data_type` cuối cùng**, phản ánh cách hệ thống hiểu column.

Ít nhất hỗ trợ:

```text
TEXT
CATEGORY
INTEGER
NUMBER
DECIMAL
BOOLEAN
DATE
TIME
DATETIME
```

Rà soát enum/API hiện tại để bổ sung `CATEGORY` nếu chưa có.

### Một số rule tối thiểu

#### Identifier-like numeric values

Các giá trị chỉ gồm số không mặc định đồng nghĩa với INTEGER.

Cần cân nhắc:

- column name;
- distinct ratio;
- fixed length;
- leading zero;
- pattern của value;
- khả năng đây là ID/code/số hồ sơ/mã định danh.

Ví dụ:

```text
Số hồ sơ = 15020001
```

phải có khả năng trở thành:

```text
TEXT
```

#### CATEGORY

Không được dùng rule đơn giản:

```text
distinct_count thấp → CATEGORY
```

Phải xét thêm:

- column name;
- distinct ratio;
- số lượng row;
- average text length;
- sample values;
- distribution.

Các column dạng `Ghi chú`, `Note`, `Description`, nội dung tự do không được tự động chuyển thành CATEGORY chỉ vì dataset hiện tại có ít distinct values.

#### DATE / DATETIME

Hỗ trợ nhiều format phổ biến, ví dụ:

```text
YYYY-MM-DD
YYYY-MM-DD HH:mm:ss
DD/MM/YYYY
DD-MM-YYYY
DD/MM/YYYY HH:mm:ss
```

Không hardcode chỉ duy nhất một format.

## 7. LLM ColumnTypeClassifier

Không tạo thêm `SourceDataAgent`.

Tạo một component/service nhỏ chuyên phân loại type cho các column ambiguous.

Ví dụ:

```text
ColumnTypeClassifier
```

Nó có thể gọi LLM một lần với structured output.

Chỉ gọi khi rule-based inference không đủ chắc chắn.

Input tối thiểu có thể gồm:

```text
column_name
duckdb_type
sample_values
null_ratio
distinct_count
distinct_ratio
average_length
candidate_type
```

Output phải bị giới hạn vào enum data type hợp lệ.

Ví dụ:

```json
{
  "data_type": "TEXT",
  "confidence": 0.93
}
```

Không cho LLM trả type tự do ngoài enum.

Không gửi toàn bộ CSV lên LLM.

Chỉ gửi metadata và số lượng sample values giới hạn.

## 8. Thời điểm phân tích CSV

Không thực hiện full source analysis ngay khi User upload file.

Khi upload chỉ thực hiện các validation tối thiểu cần thiết để lưu file, ví dụ:

- extension/file type;
- file readable;
- file size;
- encoding/header cơ bản;
- giới hạn số lượng file.

Không chạy full DuckDB profiling + LLM classification ở bước upload.

Full analysis chỉ chạy sau khi User nhấn:

```text
Lưu và phân tích
```

trên Project Init/Project Detail.

Flow mong muốn:

```text
User chỉnh Raw Requirement
+
Upload/Delete CSV
        ↓
Save & Analyze
        ↓
DuckDB Parser
        ↓
Profiler
        ↓
Logical Type Inference
        ↓
LLM ColumnTypeClassifier nếu cần
        ↓
SchemaMetadata
        ↓
RequirementAgent
        ↓
Requirements / AnalyticalRequirements
```

Sau khi analysis hoàn thành, Frontend refresh lại Requirements và Data Source metadata.

## 9. Backend/API cần rà soát

OpenAPI hiện tại đang:

- phân tích CSV ngay trong endpoint upload;
- cho phép update Structured Requirement;
- chưa có `CATEGORY` trong `UpdateDataSourceColumnRequest.data_type`.

Hãy rà soát và refactor API contract nếu cần để đồng bộ với behavior mới.

Không sửa generated Frontend API code thủ công.

Sau khi thay đổi Backend:

```text
export OpenAPI
→ regenerate Frontend SDK
```

theo coding guidelines hiện tại.

## 10. Yêu cầu triển khai

- Tận dụng component/shadcn hiện có trước khi tự viết mới.
- Tất cả clickable element phải có hover state và `cursor-pointer`.
- Có Skeleton khi initial loading.
- Có Empty State và Error State phù hợp.
- Không hardcode UI text; cập nhật i18n namespace tương ứng.
- Không dùng `any`.
- Không duplicate API types.
- Giữ đúng FSD/Clean Architecture hiện tại.
- Không tạo Agent mới nếu nhiệm vụ chỉ cần một structured LLM classification call.
- Viết test cho logic type inference, đặc biệt các case:
  - numeric identifier → TEXT;
  - free-text note không bị CATEGORY;
  - low-cardinality categorical column → CATEGORY;
  - DD/MM/YYYY → DATE;
  - datetime phổ biến → DATETIME;
  - leading-zero identifier → TEXT;
  - ambiguous column được chuyển sang LLM classifier;
  - classifier output ngoài enum phải bị reject.
