# Tài liệu Mô tả Kiến trúc System & Luồng Dữ liệu (Data Flow Diagram)

## 1. Tổng quan Hệ thống
Hệ thống là một quy trình tự động hóa thiết kế Kho dữ liệu (Data Warehouse Design) sử dụng các **LLM Agent** kết hợp với kiểm duyệt an toàn dữ liệu (**PII Guard**), kiểm tra lỗi tự động (**Validation Engine**), kiểm thử tự động trên môi trường giả lập (**Sandbox**) và sự can thiệp/phê duyệt của con người (**Human Review**).

---

## 2. Các Thành phần chính trong Hệ thống

### 2.1. Giao diện & Người dùng (Frontend & User)
* **User**: Người dùng cuối gửi yêu cầu, prompt điều chỉnh, tải file SQL và nhận kết quả sinh mã cuối cùng.
* **Chỗ nhập dữ liệu đầu vào (Input Data Form)**: Tiếp nhận `Requirement/Source Data` từ User.
* **Chỗ nhập prompt (Prompt Form)**: Tiếp nhận `Prompt` chỉ thị từ User.
* **Chức năng Tải File SQL**: Cho phép người dùng xuất và tải file SQL (DDL/DML) trực tiếp từ mã DBML.

### 2.2. Xử lý Backend & Lưu trữ (Backend & PostgreSQL)
* **Backend**: Tiếp nhận dữ liệu từ các form Frontend, đẩy dữ liệu thô vào CSDL và gửi prompt đến Agent điều phối.
* **PostgreSQL**: Cơ sở dữ liệu trung tâm lưu trữ:
  * Raw Requirements (Yêu cầu thô)
  * Source Data (Dữ liệu nguồn thô)
  * `data_models`: Lưu trữ mã DBML chính thức/hiện tại của hệ thống.
  * `data_model_changes`: Lưu trữ lịch sử đề xuất thay đổi mô hình dữ liệu (trạng thái `PROPOSED`, `base_revision=N`).

### 2.3. Hệ thống Agent AI (LLM Multi-Agent System)
* **Agent điều phối (Orchestration Agent)**: Tiếp nhận Prompt từ Backend và quản lý luồng thực thi, vòng lặp thử lại (retry/update) của các Agent con.
* **RequirementAgent**: Rút trích và làm rõ các yêu cầu từ dữ liệu thô trong PostgreSQL.
* **SourceDataAgent**: Phân tích cấu trúc dữ liệu nguồn lấy từ PostgreSQL.
* **DWDesignAgent**: Tổng hợp các yêu cầu phân tích và dữ liệu nguồn đã phân tích để thiết kế mô hình Data Warehouse (xuất ra định dạng DBML).

### 2.4. Bảo mật & Tương tác với LLM API
* **PII Guard**: Thành phần lọc và ẩn danh dữ liệu nhạy cảm (Personally Identifiable Information) trước khi gửi tới LLM.
* **LLM API**: Mô hình ngôn ngữ lớn xử lý yêu cầu.
  * *Luồng*: `Agent` ➔ `PII guard` ➔ `masked` ➔ `LLM API` ➔ `completion` ➔ `PII guard` ➔ `Agent`.

### 2.5. Kiểm định & Đánh giá (Validation & Human Review)
* **AnalyticalRequirement**: Tệp/Cấu trúc yêu cầu phân tích trung gian được kết hợp từ `Requirements` và `Source Data đã được phân tích`.
* **Validate / ValidationEngine**: Động cơ kiểm tra tính đúng đắn về mặt cú pháp và logic của DBML.
* **HumanReview**: Vòng kiểm duyệt cuối cùng bởi con người trước khi đưa vào sản xuất.
* **Codegen**: Công cụ sinh mã nguồn (SQL/DDL/ETL...) từ DBML đã được phê duyệt.

---

## 3. Chi tiết Luồng Dữ liệu (Data Flow Steps)

### Bước 1: Tiếp nhận Đưa dữ liệu đầu vào
1. **User** gửi `Requirement/Source Data` vào **Chỗ nhập dữ liệu đầu vào** và nhập `Prompt` vào **Chỗ nhập prompt**.
2. **Chỗ nhập dữ liệu đầu vào** gửi dữ liệu đến **Backend**, sau đó **Backend** chuyển tiếp `Lưu Data` vào **PostgreSQL**.

### Bước 2: Xử lý Yêu cầu & Dữ liệu nguồn qua Agents
1. **Agent điều phối** kích hoạt **RequirementAgent** và **SourceDataAgent**:
   * **RequirementAgent** thực hiện `Lấy Raw Requirement` từ **PostgreSQL**.
   * **SourceDataAgent** thực hiện `Lấy Source Data` từ **PostgreSQL**.
2. Cả hai Agent này tương tác qua lại với **PII guard** để bảo mật dữ liệu trước khi gửi sang **LLM API**.
3. **RequirementAgent** tạo ra kết quả `Requirements`:
   * Ban đầu **RequirementAgent** sẽ phân tích `Raw Requirement` để tạo thành `Requirements` lưu vào **PostgreSQL**.
   * Chuyển thông tin `Requirements` cùng với `Source Data đã được phân tích` cho **RequirementAgent** để hỗ trợ phân tích thành **AnalyticalRequirement**.
4. **SourceDataAgent** tạo ra `Source Data đã được phân tích`:
   * Đẩy thông tin tới cho **RequirementAgent** để tạo ra **AnalyticalRequirement**.
   * Đẩy thông tin trực tiếp tới **DWDesignAgent**.

### Bước 3: Thiết kế Mô hình Kho dữ liệu (DW Design)
1. **DWDesignAgent** tổng hợp dữ liệu từ:
   * **AnalyticalRequirement**
   * **Source Data đã được phân tích**
   * Kết quả xử lý an toàn từ **PII guard** / **LLM API**.
2. **DWDesignAgent** thực hiện:
   * Xuất cấu trúc `DBML` tới bước **Validate**.

### Bước 4: Kiểm tra Cú pháp & Chạy thử nghiệm Sandbox
1. Cấu trúc `DBML` được gửi qua **Validate / ValidationEngine** để kiểm tra cú pháp:
   * **Nếu cú pháp NOT OK**: Gửi thông báo lỗi qua luồng `retry` về **Agent điều phối** để tái tạo lại thiết kế.
2. Nếu cú pháp hợp lệ, mã DBML sẽ được đưa vào môi trường **Sandbox** để chạy thử nghiệm mã DDL/SQL:
   * **Nếu Sandbox NOT OK (xảy ra lỗi runtime/thực thi)**: Trả phản hồi lỗi về **Agent điều phối** để retry.
   * **Nếu Sandbox OK (chạy thử nghiệm thành công)**: Chuyển toàn bộ dữ liệu DBML và trạng thái OK sang bước **HumanReview**.

### Bước 5: Đánh giá bởi Con người & Phê duyệt (Human Review)
1. Người dùng/Chuyên gia kiểm tra mã DBML đã được kiểm thử thành công từ Sandbox tại **HumanReview**:
   * **Trường hợp cần chỉnh sửa**:
     1. Người dùng nhập `prompt` mới và gửi yêu cầu cho **Agent điều phối** để tái chạy luồng xử lý.
     2. Đề xuất mới của Agent sẽ được ghi vào bảng `data_model_changes` với trạng thái `PROPOSED` và `base_revision=N`.
     3. Nếu người dùng chọn **`approved`** đề xuất: Hệ thống sẽ cập nhật DBML mới từ bảng `data_model_changes` vào bảng `data_models`.
     4. Nếu người dùng chọn **`rejected`** đề xuất: Giữ nguyên DBML cũ trong bảng `data_models`.
   * **Trường hợp không cần chỉnh sửa**: Giữ nguyên mã DBML hiện tại trong bảng `data_models`.

### Bước 6: Sinh mã (Codegen), Tải SQL & Trả kết quả
Nếu người dùng muốn, họ có thể:
1. Dữ liệu `DBML` chính thức lưu trong bảng `data_models` trong **PostgreSQL** được đưa vào mô-đun **Codegen**.
2. **Codegen** biên dịch sơ đồ DBML thành mã SQL hoàn chỉnh (DDL/DML):
   * Cung cấp **Chức năng tải file SQL từ DBML** giúp người dùng tải trực tiếp tệp script SQL về máy.
   * Trả kết quả sinh mã cuối cùng về giao diện cho **User**.

---

## 4. Tóm tắt Bảng Tương tác Thành phần

| Nguồn (From) | Đích (To) | Loại dữ liệu / Hành động (Data / Action) |
| :--- | :--- | :--- |
| **User** | Chỗ nhập dữ liệu đầu vào | Requirement / Source Data |
| **User** | Chỗ nhập prompt | Prompt |
| **Backend** | PostgreSQL | Lưu Data (`Raw Requirement`, `Source Data`) |
| **Backend** | Agent điều phối | Prompt chỉ thị |
| **PostgreSQL** | RequirementAgent | Lấy Raw Requirement |
| **PostgreSQL** | SourceDataAgent | Lấy Source Data |
| **Agent / PII guard** | LLM API | masked ➔ completion |
| **RequirementAgent** | AnalyticalRequirement | Requirements |
| **SourceDataAgent** | DWDesignAgent / RequirementAgent | Source Data đã được phân tích |
| **DWDesignAgent** | Validate | DBML |
| **ValidationEngine / Sandbox** | Agent điều phối | NOT OK Text (retry khi lỗi cú pháp hoặc lỗi runtime Sandbox) |
| **ValidationEngine / Sandbox** | HumanReview | Chuyển tiếp khi **Validation OK** & **Sandbox OK** |
| **HumanReview** | Agent điều phối | Prompt chỉnh sửa ➔ Ghi `data_model_changes` (`PROPOSED`) |
| **HumanReview** | PostgreSQL (`data_models`) | Cập nhật DBML khi `approved` |
| **PostgreSQL (`data_models`)** | Codegen | DBML chính thức |
| **Codegen** | User / Frontend | Trả mã hoàn chỉnh & Cho phép **Tải file SQL** |