# Tài Liệu Yêu Cầu Nghiệp Vụ — Quản Lý & Phân Tích Hồ Sơ Bệnh Án (Y Tế)

> **Mã bài toán:** DW-HEALTHCARE-01  
> **Lĩnh vực (Domain):** Y tế / Quản lý Bệnh viện (Healthcare & Hospital Information System)  
> **Dữ liệu nguồn kèm theo:** 4 tệp CSV trong thư mục `eval/sample/` (`DanhSachBenhNhan.csv`, `ThongTinBenhNhan.csv`, `ThongtinHoSoLuuTru.csv`, `DanhSachHoSoLuuTru.csv`)

---

## 📋 Toàn Văn Yêu Cầu Nghiệp Vụ (Raw Requirement)

Bệnh viện cần xây dựng Kho dữ liệu (Data Warehouse) để quản lý và phân tích hồ sơ bệnh án lưu trữ, phục vụ các mục tiêu sau:

1. **Phân tích tình hình khám chữa bệnh**: Theo dõi số lượng bệnh nhân, thời gian điều trị trung bình (tính từ thời gian vào viện đến ngày ra viện) phân theo từng khoa phòng (vào từ khoa nào, ra từ khoa nào), nhóm tuổi và giới tính.
2. **Quản lý đối tượng bệnh nhân**: Thống kê cơ cấu bệnh nhân theo diện chi trả (BHYT, BHYT Quân, Miễn phí, Dịch vụ) và loại hình điều trị (Nội trú, Ngoại trú).
3. **Tối ưu hóa công tác lưu trữ hồ sơ**: Quản lý vị trí vật lý lưu trữ hồ sơ bệnh án (theo Kho, Tủ, Ngăn, Kệ, Ký hiệu) và trạng thái hồ sơ (đang lưu trữ, chờ đưa vào kho, cần bổ sung xét nghiệm) để phục vụ tra cứu nhanh chóng và bảo mật thông tin cá nhân của bệnh nhân.

---

## 🎯 Mục Tiêu Phân Tích Dữ Liệu (Analytical Goals)

| Chỉ số cần đo lường (Metrics / Measures) | Chiều phân tích (Dimensions) | Mức độ chi tiết (Grain) | Phương thức tổng hợp (Aggregation) |
| :--- | :--- | :--- | :--- |
| **Thời gian điều trị trung bình (ngày)** | Khoa vào viện, Khoa ra viện, Nhóm tuổi, Giới tính | Từng lượt điều trị / bệnh án | `AVG(DATEDIFF(ngay_ra, ngay_vao))` |
| **Số lượng bệnh nhân tiếp nhận** | Diện đối tượng chi trả, Loại hình điều trị (Nội/Ngoại trú) | Từng bệnh nhân / Lượt vào viện | `COUNT(DISTINCT so_ho_so)` |
| **Số lượng hồ sơ lưu trữ theo trạng thái** | Trạng thái hồ sơ, Vị trí Kho, Tủ, Ngăn, Kệ | Từng hồ sơ bệnh án lưu trữ | `COUNT(so_benh_an)` |

---

## 🔒 Yêu Cầu Kỹ Thuật & Bảo Mật (Technical & Security Constraints)
- **Ẩn danh hóa dữ liệu (PII Protection)**: Thông tin cá nhân nhạy cảm của bệnh nhân (Họ và tên, Địa chỉ chi tiết) phải được PII Guard ẩn danh trước khi chuyển qua LLM API.
- **Khóa thay thế (Surrogate Keys)**: Toàn bộ bảng Fact và Dimension trong Data Warehouse phải sử dụng Surrogate Key dạng số nguyên hoặc UUID (ví dụ: `benhnhan_sk`, `khoa_sk`, `vitri_sk`) thay vì dùng trực tiếp số hồ sơ y tế.
- **Chuẩn hóa mô hình**: Thiết kế theo mô hình hình sao (Star Schema) tối ưu truy vấn OLAP, liên kết khóa ngoại rõ ràng.
