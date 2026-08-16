# Weekly Journal — Team [Tên Team]

> Ghi lại mỗi tuần: học được gì, khó khăn gì, quyết định gì, kế hoạch tiếp.

---

## Week 1: 2026-08-10 - 2026-08-16

### Mục tiêu tuần này
- [x] Triển khai UC9.1: Chỉnh sửa cấu hình Sandbox Database (PostgreSQL, BigQuery, Snowflake, MySQL...)
- [x] Triển khai UC9.2: Chạy thử DDL script trên Sandbox DB đã cấu hình & hiển thị log Terminal

### Đã hoàn thành
- Hoàn thành bộ API backend Clean Architecture tại `src/presentation/api/v1/sandbox.py`.
- Driver executor thực thi DDL phân tách statement và đo thời gian từng câu lệnh SQL.
- Giao diện UI Frontend FSD với SandboxConfigCard, DdlActionsBar, DdlCodeEditor, ExecutionTerminal.
- Viết bộ unit test `tests/test_sandbox.py` vượt qua 100% test cases.

### Khó khăn & Giải pháp
| Khó khăn | Giải pháp | Kết quả |
|----------|-----------|---------|
| Đa dạng hệ CSDL Sandbox | Thiết kế Driver Adapter pattern với fallback an toàn | Hỗ trợ PostgreSQL và driver linh hoạt cho các RDBMS khác |

### Bài học
- Tuân thủ Clean Architecture và FSD giúp tách biệt rõ ranh giới giữa logic thực thi DB và giao diện Terminal log UI.

---

## Week 2: [Ngày bắt đầu] - [Ngày kết thúc]

### Mục tiêu tuần này
- [ ] [Mục tiêu 1]

### Đã hoàn thành
-

### Khó khăn & Giải pháp
| Khó khăn | Giải pháp | Kết quả |
|----------|-----------|---------|
| | | |

### Bài học
-

### Kế hoạch tuần sau
-

---

<!-- Tiếp tục copy block trên cho Week 3, 4, 5, 6 -->

## Technical decision - 2026-08-13

- Đóng gói UC5.3 thành feature `analysis` độc lập theo FSD; `app/page.tsx` chỉ chịu trách nhiệm định tuyến và khởi tạo workspace.
- Chuẩn hóa dữ liệu diễn giải bằng TypeScript interface để có thể thay dữ liệu mẫu bằng response từ API mà không thay cấu trúc component.
- Hiển thị Grain, lý do chọn khóa và cảnh báo theo từng bảng; mỗi nhóm có thể thu gọn để nội dung dài vẫn dễ đọc.
- Đồng bộ Tailwind lên v4 để khớp `@tailwindcss/postcss` và cú pháp `@import "tailwindcss"` của Next.js 16.
