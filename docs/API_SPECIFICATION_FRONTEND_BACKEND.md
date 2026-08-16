# ĐẶC TẢ API SPECIFICATION (JSON FORMAT): KẾT NỐI FRONTEND & BACKEND

## I. TỔNG QUAN VÀ THỎA THUẬN CHUNG (GENERAL AGREEMENTS)

Tài liệu này quy định giao thức kết nối RESTful API truyền nhận dữ liệu định dạng **JSON (JavaScript Object Notation)** giữa hệ thống **Frontend (Web Application)** và **Backend Core Multi-Agent System (FastAPI / LangGraph)**.

### 1. Base URL & Giao Thức
- **Development Base URL:** `http://localhost:8001/api/v1`
- **Production Base URL:** `https://.../api/v1`

### 2. Standard HTTP Request Headers
Mọi yêu cầu gửi từ Frontend tới Backend đều phải đi kèm các Headers chuẩn sau:

| Header Name | Type | Value / Example | Mô Tả |
|-------------|------|-----------------|-------|
| `Content-Type` | string | `application/json` | Đánh dấu định dạng dữ liệu payload gửi đi |
| `Accept` | string | `application/json` | Đánh dấu định dạng dữ liệu mong muốn nhận về |
| `Authorization` | string | `Bearer eyJhbGciOiJKV...` | Token xác thực JWT khi bật Auth |
| `X-Request-ID` | string | `req_9a8b7c6d-5e4f` | ID duy nhất của request phục vụ Tracing / Logging |
| `X-Client-Version` | string | `1.0.0` | Phiên bản giao diện Frontend Client |

---

## II. CAO TRÚC PHẢN HỒI CHUẨN (STANDARD RESPONSE ENVELOPE)

Tất cả các API Response trả về từ Backend (dù Thành công hay Thất bại) đều tuân thủ cấu trúc khung chuẩn hóa **Envelope Pattern**:

### 1. Cấu Trúc Thành Công (Success Envelope - Status 200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Mô tả ngắn gọn kết quả xử lý thành công",
  "data": {
    /* Payload dữ liệu chính trả về cho Frontend */
  }
}
```

### 2. Cấu Trúc Lỗi (Error Envelope - Status 400 / 422 / 500 / ...)

```json
{
  "code": 400,
  "message": "Thông điệp báo lỗi chi tiết cho người dùng",
  "error_code": "INVALID_INPUT_SCHEMA", // Tự định nghĩa
  "details":
  [
    {
      "field": "business_requirements",
      "message": "Ký tự mô tả phải từ 10 đến 15000 ký tự"
    }
  ]
}
```
