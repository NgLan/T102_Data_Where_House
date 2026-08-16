# Weekly Journal — Team [Tên Team]

> Ghi lại mỗi tuần: học được gì, khó khăn gì, quyết định gì, kế hoạch tiếp.

---

## Week 1: [Ngày bắt đầu] - [Ngày kết thúc]

### Mục tiêu tuần này
- [ ] [Mục tiêu 1]
- [ ] [Mục tiêu 2]
- [ ] [Mục tiêu 3]

### Đã hoàn thành
- [thành quả 1]
- [thành quả 2]

### Khó khăn & Giải pháp
| Khó khăn | Giải pháp | Kết quả |
|----------|-----------|---------|
| [mô tả] | [cách xử lý] | [output] |

### Bài học
- [bài học 1]
- [bài học 2]

### Kế hoạch tuần sau
- [ ] [task 1]
- [ ] [task 2]

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
