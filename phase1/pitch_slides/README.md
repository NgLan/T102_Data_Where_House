# DATA WHERE HOUSE? — Video Pitch Slide Deck (1 Phút)

Slide trình chiếu phục vụ quay video giới thiệu sản phẩm **Data Where House?** trong vòng ~1 phút theo kịch bản chuẩn tại `phase1/Script giới thiệu Data Where House_ — khoảng 1 phút.md`.

---

## 🎨 Cấu Trúc File Chuẩn Hóa (Clean Architecture, SRP, DRY)

```
phase1/pitch_slides/
├── index.html              # HTML master container kết nối các module
├── css/
│   ├── variables.css       # Token màu, font, bóng đổ comic ink, kích thước 16:9
│   ├── base.css            # Khung hiển thị tỉ lệ 16:9 (1280x720), grid giấy vẽ, auto scale
│   ├── typography.css      # Font Montserrat, Be Vietnam Pro, Caveat handwriting & Wordmarks
│   ├── components.css      # Cards, pipeline flow, placeholder ảnh, code box, punchline
│   └── animations.css      # Hiệu ứng mượt mà (staggered pop-in, comic wiggle, pulse badge)
├── js/
│   ├── engine.js           # Engine chuyển slide bằng phím, responsive auto-fit màn hình
│   └── presenter.js        # Hỗ trợ đếm giờ tập dượt (60s timer), phím tắt quay video
└── README.md
```

---

## ⌨️ Phím Tắt Điều Khiển Khi Quay Video

| Phím | Chức năng |
| :--- | :--- |
| **`Space`** hoặc **`→`** hoặc **`PageDown`** | Chuyển sang slide kế tiếp |
| **`←`** hoặc **`PageUp`** | Quay lại slide trước |
| **`F`** | Bật / Tắt chế độ toàn màn hình (Fullscreen) không viền |
| **`T`** | Bật / Tắt đồng hồ bấm giờ tập dượt (Pitch Timer 60s) |
| **`R`** | Reset về Slide 1 và đặt lại đồng hồ |
| **`1` - `7`** | Nhảy trực tiếp đến slide số tương ứng |

> 💡 **Chế độ quay video thông minh:** Chuột sẽ tự động ẩn đi sau 2.5 giây không di chuyển để tránh làm bẩn khung hình quay video. Không có nút mũi tên chuyển trang trên màn hình để giữ khung hình sạch 100%.

---

## 🖼️ Danh Sách Các Khung Ảnh Chờ (Image Placeholders)

Đã bố trí sẵn các khung ô chữ nhật với viền nét đứt và mô tả chi tiết:

1. **Slide 4 (Luồng Hoạt Động)**:
   - `[KHUNG ẢNH: Giao Diện Chat Làm Rõ Yêu Cầu & Phân Tích Dữ Liệu Nguồn]`
2. **Slide 5 (Kiểm Soát & Tinh Chỉnh)**:
   - `[KHUNG ẢNH: Sơ Đồ Mô Hình & Các Vấn Đề Được Phát Hiện]`
3. **Slide 6 (Thực Thi DDL & Sandbox)**:
   - `[KHUNG ẢNH: DDL Sinh Ra & Chạy Thử Trên Môi Trường Sandbox]`

> 💡 *Khi có ảnh chụp màn hình thực tế, chỉ cần thay thẻ `<div class="img-placeholder">` bằng `<img src="..." class="card" />`.*

---

## ⏱️ Khung Thời Gian Gợi Ý Cho Video (60 - 65 Giây)

- **Slide 1 (0:00 - 0:08)**: Ảo tưởng về sự đơn giản (Data + Req &rarr; Tables)
- **Slide 2 (0:08 - 0:18)**: Thực tế & 5 câu hỏi bế tắc (Fact vs Dim, Grain, Đúng/Sai)
- **Slide 3 (0:18 - 0:25)**: Giới thiệu giải pháp Data Where House?
- **Slide 4 (0:25 - 0:45)**: 3 Bước hoạt động của AI Agent (Làm rõ &rarr; Phân tích &rarr; Đề xuất Schema)
- **Slide 5 (0:45 - 0:53)**: Human-in-the-Loop & Quy tắc kiểm tra chất lượng
- **Slide 6 (0:53 - 0:58)**: Tự động sinh DDL & Sandbox DuckDB
- **Slide 7 (0:58 - 1:05)**: Slogan chốt & Nhận diện thương hiệu

---

## 📄 Xuất Slide Ra PDF & PowerPoint (.pptx) (Chuẩn 16:9)

- **Bản PDF**: [DATA_WHERE_HOUSE_Pitch_Slides.pdf](file:///d:/VinAI/P-102/phase1/pitch_slides/DATA_WHERE_HOUSE_Pitch_Slides.pdf)
- **Bản PowerPoint**: [DATA_WHERE_HOUSE_Pitch_Slides.pptx](file:///d:/VinAI/P-102/phase1/pitch_slides/DATA_WHERE_HOUSE_Pitch_Slides.pptx)

### 🚀 Lệnh tự động xuất lại khi cập nhật slide:

1. **Xuất PDF**:
   ```bash
   python export_pdf.py
   ```
2. **Xuất PowerPoint (.pptx)**:
   ```bash
   python export_pptx.py
   ```
   *(Tự động đồng bộ từ HTML slides, xuất slide widescreen 16:9 siêu nét)*


