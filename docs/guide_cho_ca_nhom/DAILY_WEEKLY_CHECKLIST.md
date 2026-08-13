# Hướng Dẫn Checklist Công Việc Hằng Ngày, Hằng Tuần & Deliverables

Tài liệu này cung cấp danh sách kiểm tra (checklist) công việc theo ngày, theo tuần, các mốc thời gian quan trọng và hướng dẫn chuẩn bị **10 Deliverables** nộp cho Ban Tổ Chức (BTC) AI20K.

---

## I. Mức Điểm Mục Tiêu & 5 Tiêu Chí Chấm Điểm của BTC

Mục tiêu chung của team là đạt tối thiểu **35/50 điểm** để lọt nhóm dẫn đầu. Điểm được BTC đánh giá qua 5 tiêu chí (thang điểm 10/tiêu chí):

1. **Product/Business (20%):** Giải quyết đúng nỗi đau của người dùng, có mô tả bài toán và hướng phát triển rõ ràng (Mục tiêu: ≥ 8/10).
2. **System Design (20%):** Kiến trúc hệ thống chuẩn chỉnh, sơ đồ rõ ràng, giải thích lý do chọn tech stack (Mục tiêu: ≥ 7/10).
3. **UI/UX Design (20%):** Giao diện đẹp, dễ dùng, responsive, xử lý trạng thái chờ/lỗi mượt mà (Mục tiêu: ≥ 7/10).
4. **DevOps (20%):** Có Docker, CI/CD tự động, Live URL chạy ổn định, có health check (Mục tiêu: ≥ 6-8/10 - *Tiêu chí dễ ghi điểm vượt trội*).
5. **Code Quality (20%):** Code sạch, có type hints, xử lý ngoại lệ đúng chuẩn, pass ruff lint và có test cases (Mục tiêu: ≥ 7/10).

---

## II. Checklist Công Việc Hằng Ngày (Daily Routine)

### 1. Đầu ngày (10 - 15 phút)
- [ ] Pull code mới nhất từ branch chính (`git pull origin main`).
- [ ] Kiểm tra danh sách task cá nhân trong ngày.
- [ ] Làm Daily Standup (Hôm qua làm gì? Hôm nay làm gì? Có vướng mắc gì không?).

### 2. Trong ngày (Khi lập trình)
- [ ] Tuân thủ nghiêm ngặt quy định code trong [TECHNICAL_CODING_GUIDELINES.md](file:///d:/VinAI/P-102/docs/guide_cho_ca_nhom/TECHNICAL_CODING_GUIDELINES.md).
- [ ] Chạy ruff lint để sửa lỗi định dạng code Python (`ruff check src/ tests/`).
- [ ] Viết kèm unit test cho các hàm/feature vừa hoàn thành.
- [ ] Commit code thường xuyên với message rõ ràng (ví dụ: `feat: ...`, `fix: ...`, `test: ...`). Khống gom tất cả thay đổi vào 1 commit lớn cuối ngày.

### 3. Cuối ngày (10 phút)
- [ ] Cập nhật kết quả công việc vào file [WORKLOG.md](file:///d:/VinAI/P-102/WORKLOG.md).
- [ ] Ghi 2-3 câu ngắn gọn vào file [JOURNAL.md](file:///d:/VinAI/P-102/JOURNAL.md) (nêu quyết định kỹ thuật, bài học hoặc khó khăn gặp phải).
- [ ] Push toàn bộ code lên GitHub cá nhân/team.

---

## III. Checklist Công Việc Hằng Tuần (Weekly Routine)

### 1. Đầu tuần
- [ ] Họp 2 lần/tuần để lập kế hoạch tuần (Sprint Planning), phân công người chịu trách nhiệm cho từng mục tiêu của tuần.
- [ ] Rà soát và cập nhật tiến độ các tính năng chính.

### 2. Trong tuần
- [ ] Kiểm tra trạng thái CI/CD pipeline trên GitHub Actions (đảm bảo luôn có màu xanh - pass toàn bộ lint & test).
- [ ] Đánh giá và bổ sung sơ đồ kiến trúc hoặc tài liệu API nếu có sự thay đổi về mặt thiết kế hệ thống.

### 3. Cuối tuần
- [ ] Tổng kết nhật ký phát triển hàng tuần trong [JOURNAL.md](file:///d:/VinAI/P-102/JOURNAL.md).
- [ ] Rà soát lại danh sách 10 deliverables đối chiếu với tiêu chí chấm của BTC.

---

## IV. Danh Sách 10 Deliverables & Vị Trí Nộp Trong Repo

Phần lớn các đội mất điểm vì nộp thiếu deliverables. Hoàn thành trọn vẹn 10/10 mục dưới đây giúp dự án đạt điểm tối đa ở phần hoàn thiện:

| # | Deliverable | Vị trí file trong Repo | Nội dung cần có |
|---|---|---|---|
| 1 | **Source Code** | `/src/`, `/backend/`, `/frontend/` | Code sạch, chạy được sau khi setup `.env`, có type hints, không secrets |
| 2 | **README.md** | `/README.md` | Giới thiệu bài toán, giao diện app, hướng dẫn cài đặt, tech stack, team |
| 3 | **Architecture Diagram** | `/docs/architecture.md` (hoặc `.png`) | Sơ đồ kiến trúc thể hiện luồng dữ liệu giữa Frontend, Backend, Agent, DB |
| 4 | **AI Logs** | LangSmith Link hoặc screenshot log | Bằng chứngAgent reasoning (LLM call, retrieval, tool calls) |
| 5 | **Live URL** | Link ghi trong `/README.md` | Đường link ứng dụng đã deploy chạy thực tế trên Internet (Vercel, Render...) |
| 6 | **Video Demo** | `/docs/video-demo.md` | Link video YouTube 3-5 phút giới thiệu team và demo các tính năng chính |
| 7 | **Pitch Deck** | `/docs/pitch-deck.pdf` | Slide thuyết trình 10 trang chuẩn bị cho Demo Day |
| 8 | **Development Journal** | `/JOURNAL.md` | Nhật ký ghi lại các quyết định kỹ thuật và bài học kinh nghiệm |
| 9 | **Worklog** | `/WORKLOG.md` | Nhập lịch sử làm việc hằng ngày của từng thành viên |
| 10 | **Evaluation Evidence** | `/docs/evaluation.md` (hoặc `/eval/`) | Bằng chứng đánh giá chất lượng agent (kết quả test, metrics RAGAS...) |

---

## V. Top 10 Lỗi Cần Tránh (Rút Kinh Nghiệm Từ Các Đội Cohort 1)

Hãy luôn tự kiểm tra code và dự án để không mắc phải 10 lỗi phổ biến sau:

1. **Bare except:** Bắt ngoại lệ kiểu `except:` hoặc `except Exception:` rồi cho `pass`. -> *Khắc phục:* Bắt exception cụ thể và ghi log.
2. **Hardcoded secrets:** Dán trực tiếp API key hay password vào code. -> *Khắc phục:* Đưa toàn bộ vào `.env`.
3. **Không viết test:** Không có file test nào trong thư mục `tests/`. -> *Khắc phục:* Viết ít nhất 5-10 test cases chính.
4. **Thiếu CI/CD:** Không cấu hình GitHub Actions tự động kiểm tra code. -> *Khắc phục:* Tạo file `.github/workflows/ci.yml`.
5. **Hàm quá dài:** Viết 1 hàm dài hàng trăm dòng. -> *Khắc phục:* Tách thành các hàm nhỏ dưới 30 dòng.
6. **Gom tất cả code vào 1 file:** File `main.py` hay `app.py` dài hơn 500 dòng. -> *Khắc phục:* Chia nhỏ code theo đúng kiến trúc.
7. **Không sử dụng type hints:** Khó bảo trì và dễ sinh lỗi ngầm. -> *Khắc phục:* Khai báo kiểu dữ liệu cho 100% các hàm.
8. **README qua sơ:** Thiếu hướng dẫn chạy, thiếu hình ảnh demo. -> *Khắc phục:* Đầu tư viết README chỉn chu.
9. **Thiếu Architecture Diagram:** Không vẽ sơ đồ tổng quan hệ thống khiến BTC đánh giá thấp điểm System Design.
10. **Bỏ qua Evaluation Evidence:** Không đo đạc hay đưa ra bằng chứng đánh giá độ chính xác của AI agent.
