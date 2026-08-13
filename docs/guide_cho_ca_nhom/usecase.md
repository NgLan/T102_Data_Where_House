### **UC3. Quản lý dữ liệu đầu vào**

| Mã | Use case | Actor | Làm gì? | Kết quả | Ai làm |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **UC3.3** | Tải lên Data Source/Requirement | User | User chọn và tải lên tối đa 20 file dữ liệu nguồn | Danh sách Data Source được lưu vào Project, sẵn sàng phân tích | Giang |
| **UC3.5** | Chỉnh sửa dữ liệu đầu vào | User | User tạo/cập nhật lại Requirement, Business Rule/KPI | Dữ liệu đầu vào được cập nhật theo thay đổi của User | Giang |
| **UC3.6** | Xóa Data Source/Requirement | User | User xóa một Data Source/Requirement không còn cần thiết | Dữ liệu tương ứng bị loại khỏi ngữ cảnh phân tích | Giang |

### **UC5. Quản lý Data Model / DDL**

| Mã | Use case | Actor | Làm gì? | Kết quả | Ai làm |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **UC5.1.1** | Chỉnh sửa mã DBML thủ công | User | User trực tiếp gõ/sửa mã DBML trên editor | Mã DBML được cập nhật ngay theo thao tác gõ tay | Giang |
| **UC5.1.2** | Chỉnh sửa mã DBML bằng AI | User | User nhập yêu cầu bằng ngôn ngữ tự nhiên (VD: "tách Dim\_Doctor...") | Mã DBML được AI cập nhật lại theo yêu cầu của User | Lan |
| **UC5.1.3** | Chỉnh sửa bảng trên giao diện | User | User sửa trực tiếp thông số, thêm cột,... trên giao diện | Mã DBML được cập nhật lại. | Lan |
| **UC5.2.1** | Xem giao diện ERD | User | User xem sơ đồ ERD trực quan, phóng to thu nhỏ sơ đồ | Sơ đồ ERD phản ánh đúng trạng thái mã DBML hiện tại | Lan |
| **UC5.2.2** | Chọn đối tượng trên ERD | User | User kéo thả đối tượng trên sơ đồ ERC | Sơ đồ ERD phản ánh đúng trạng thái mã DBML hiện tại | Lan |
| **UC5.3** | Xem nội dung phân tích | User | User mở phần diễn giải của AI (Grain, lý do chọn khóa, cảnh báo lỗi...) | Nội dung phân tích được hiển thị đầy đủ cho User tham khảo | QAnh |
| **UC5.4** | Xem mã DDL | User | User xem mã DDL được sinh từ mô hình hiện tại | Mã DDL tương ứng với DBML hiện tại được hiển thị | QAnh |
| **UC5.5** | Tải xuống file SQL | User | User chọn Hệ quản trị cơ sở dữ liệu, nhấn nút tải file DDL dạng .sql (Nhiều loại sql khác nhau) | File .sql được lưu về máy User, tương thích với hệ quản trị đã chọn | Nam |

### **UC6. Review & duyệt đề xuất thay đổi Data Model (Proposal)**

| Mã | Use case | Actor | Làm gì? | Kết quả | Ai làm |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **UC6.1** | Xem đề xuất thay đổi | User | User xem DBML được đề xuất (như code khi được agent thay đổi sẽ có chỗ đỏ, chỗ xanh) khi yêu cầu agent thay đổi | Nội dung đề xuất, và base revision được hiển thị | Nam |
| **UC6.2** | Chấp nhận đề xuất (Accept) | User | User đồng ý áp dụng đề xuất vào Data Model hiện tại | Nếu base\_revision khớp revision hiện tại: DBML được áp dụng, revision tăng, Proposal chuyển ACCEPTED | Nam |
| **UC6.3** | Từ chối đề xuất (Reject) | User | User không đồng ý với đề xuất | Proposal chuyển REJECTED, Data Model hiện tại không thay đổi | Nam |

### **UC9. Quản lý Sandbox**

| Mã | Use case | Actor | Làm gì? | Kết quả | Ai làm |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **UC9.1** | Chỉnh sửa cấu hình Sandbox | User | User thiết lập/thay đổi thông tin kết nối đến Sandbox DB | Cấu hình Sandbox được lưu và sẵn sàng để chạy thử | QAnh |
| **UC9.2** | Chạy thử DDL | User | User nhấn nút thực thi để chạy DDL trên Sandbox DB đã cấu hình | Kết quả thực thi (thành công/lỗi \+ log) được hiển thị cho User | QAnh |
