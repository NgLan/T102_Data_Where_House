# Checklist Demo Day — Data Where House?

> Mục tiêu: ưu tiên các việc giúp đạt **8–10 điểm** ở từng tiêu chí.  
> Đánh giá hiện trạng dựa trên **tài liệu kiến trúc, yêu cầu, API và quy định code hiện có**. Những mục ghi “chưa có minh chứng” nghĩa là chưa thấy bằng chứng rõ trong tài liệu hiện tại.

## 1. Tổng hợp theo tiêu chí

| Tiêu chí | Muốn điểm cao cần có | Hiện tại | Còn thiếu / chưa rõ | Việc cần làm |
|---|---|---|---|---|
| **A1. Bài toán – Giải pháp** | Người dùng rõ; pain point có số liệu; ≥5 người dùng/chuyên gia; so sánh cách làm cũ; có người dùng thử; đo được thời gian/lỗi giảm | Bài toán và hướng giải pháp khá rõ | **Thiếu nghiên cứu người dùng, số liệu pain point, số liệu cải thiện, so sánh công cụ hiện tại, ROI** | 1) Phỏng vấn ≥5 người. 2) Ghi thời gian làm thủ công. 3) Cho họ thử hệ thống. 4) Đo thời gian/lỗi trước–sau. 5) Chốt 2–3 con số đưa lên slide |
| **A2. Tư duy sản phẩm & trình bày** | Pitch rõ: bài toán → người dùng → giải pháp → demo → bằng chứng → giới hạn → bước tiếp theo; demo theo 1 kịch bản thật | Có tài liệu yêu cầu và luồng sản phẩm khá đầy đủ | **Thiếu câu chuyện pitch ngắn gọn, số liệu giá trị, User Story gọn, giới hạn/rủi ro/bước tiếp theo** | 1) Chốt 1 persona. 2) Chốt 1 kịch bản demo xuyên suốt. 3) Viết 5–7 User Story lõi. 4) Chuẩn bị slide giới hạn/rủi ro. 5) Chuẩn bị câu trả lời phản biện |
| **B1. Kỹ thuật & kiến trúc** | Kiến trúc rõ; AI Agent đúng vai trò; Human-in-the-Loop; guardrail; xử lý lỗi; retry/timeout; eval có metric; trace; theo dõi độ trễ/lỗi/chi phí | **Mạnh:** RequirementAgent, DWDesignAgent, Validation Engine, Proposal Accept/Reject, Sandbox, retry, logging/tracing, kiến trúc phân tầng | **Thiếu lớn nhất: eval pipeline + số liệu; chưa thấy minh chứng prompt injection; chưa có bảng chi phí/độ trễ/chất lượng model; giám sát vận hành chưa đầy đủ** | 1) Làm bộ eval. 2) Đo accuracy/pass rate. 3) Đo latency/token/chi phí. 4) Thêm test prompt injection. 5) Làm dashboard/log tổng hợp lỗi và số ca cần người duyệt |
| **B2. Chất lượng triển khai** | Có URL online; tài khoản demo ≥2 vai trò; tính năng lõi chạy ổn; test có kết quả; dữ liệu xấu không làm vỡ hệ thống | API và chức năng lõi khá đầy đủ; có Sandbox và xử lý lỗi | **Chưa có minh chứng URL công khai, tài khoản demo 2 vai trò, bảng tính năng → minh chứng → kết quả, tỷ lệ test pass, test dữ liệu xấu/baseline** | 1) Deploy ổn định. 2) Tạo 2 tài khoản demo khác quyền. 3) Viết test kịch bản chính + ca lỗi. 4) Chụp/ghi kết quả. 5) Tạo bảng minh chứng |
| **B3. UI/UX** | Người mới tự làm được; đủ trạng thái chờ/rỗng/lỗi; từ ngữ dễ hiểu; AI output dễ sửa/duyệt; có test người dùng | Luồng Requirement → Data Model → Proposal → Sandbox đã có định hướng rõ | **Chưa có số liệu usability; chưa có bằng chứng test người dùng; cần rà lại loading/rỗng/lỗi, nhãn kỹ thuật, ca dữ liệu dài/rỗng/quyền khác nhau** | 1) Cho 5 người dùng thử. 2) Đo thời gian hoàn thành. 3) Ghi lỗi họ gặp. 4) Sửa nút/nhãn khó hiểu. 5) Kiểm tra loading/empty/error ở mọi màn chính |
| **B4. Chất lượng code** | Repo dễ bàn giao; README chạy được; test; lint/CI; secret an toàn; PR/review rõ; giải thích phần AI sinh và phần người sửa | **Mạnh:** quy định Clean Architecture, SRP/DRY, lint/test, secret, logging, OpenAPI, chuẩn FE/BE rất rõ | **Chưa có minh chứng README hoàn chỉnh, CI chạy tự động, PR review thật, tỷ lệ test pass, báo cáo phần code do AI hỗ trợ và cách kiểm tra** | 1) Hoàn thiện README. 2) Bật CI lint/test. 3) Giữ PR/review làm minh chứng. 4) Tổng hợp test pass. 5) Viết 1 trang “AI hỗ trợ code ở đâu và team kiểm tra thế nào” |
| **C1. Làm việc nhóm** | Phân công rõ; đúng hạn; họp đều; backlog cập nhật; có dấu vết đóng góp; tiếp thu mentor | Có phân công trong use case/tài liệu | **Thiếu hồ sơ minh chứng: biên bản họp, backlog, mốc tiến độ, phản hồi mentor → thay đổi gì, thống kê đóng góp** | 1) Gom task board. 2) Gom biên bản họp. 3) Liệt kê đóng góp từng người. 4) Ghi 3–5 góp ý mentor và thay đổi tương ứng. 5) Chuẩn bị timeline dự án |

---

## 2. Những phần hệ thống cần ưu tiên bổ sung

### Mức 1 — Rất quan trọng
- **Eval cho AI Agent**
  - Bộ câu hỏi/yêu cầu mẫu.
  - Kết quả đúng/sai rõ ràng.
  - Tỷ lệ Requirement phân tích đúng.
  - Tỷ lệ Data Model vượt Validation.
  - Tỷ lệ phải hỏi lại người dùng.
- **Số liệu trước – sau**
  - Thời gian thiết kế thủ công.
  - Thời gian dùng hệ thống.
  - Số lỗi thiết kế trước – sau.
- **Minh chứng người dùng thật**
  - Ít nhất 5 người dùng/chuyên gia.
  - Có phản hồi và thay đổi sản phẩm dựa trên phản hồi.
- **Bộ test Demo Day**
  - Happy case.
  - Requirement mơ hồ.
  - Thiếu dữ liệu nguồn.
  - Dữ liệu sai/xấu.
  - Agent lỗi.
  - Proposal Accept/Reject.
  - Sandbox chạy lỗi.

### Mức 2 — Nên làm
- Theo dõi **độ trễ, token, chi phí, tỷ lệ lỗi**.
- Test **prompt injection / rò rỉ dữ liệu**.
- Có **2 tài khoản demo khác quyền**.
- Hoàn thiện **README + CI + kết quả test**.
- Tạo trang/bảng **“Tính năng → Minh chứng → Kết quả đánh giá”**.

### Mức 3 — Nếu còn thời gian
- Ước tính chi phí vận hành.
- So sánh 2 model/provider bằng số liệu.
- Nêu phương án mở rộng hệ thống.
- Thêm số liệu UX: thời gian hoàn thành tác vụ, tỷ lệ hoàn thành.

---

## 3. Slide cần có gì?

1. **Bài toán**
   - Ai gặp vấn đề?
   - Họ đang làm gì?
   - Mất bao lâu / dễ sai ở đâu?

2. **Giải pháp**
   - Data Where House? giúp gì?
   - Vì sao cần AI Agent?
   - Không làm những gì?

3. **Luồng chính**
   - Requirement + dữ liệu nguồn
   - AI phân tích
   - Tạo Data Warehouse
   - Validation
   - Người dùng duyệt
   - ERD / DDL / tài liệu / Sandbox

4. **Kiến trúc**
   - Frontend
   - Backend
   - RequirementAgent
   - DWDesignAgent
   - Validation Engine
   - Database
   - Sandbox
   - Human-in-the-Loop

5. **Điểm kỹ thuật nổi bật**
   - Agent không tự ghi đè Data Model.
   - Có Proposal Accept/Reject.
   - Có Validation Engine.
   - Có retry/xử lý lỗi.
   - Có trace/log.
   - Có kiểm tra dữ liệu nguồn.

6. **Kết quả đánh giá**
   - Tỷ lệ đúng.
   - Tỷ lệ Validation pass.
   - Thời gian xử lý.
   - Thời gian tiết kiệm.
   - Số lỗi giảm.

7. **Người dùng thử**
   - Số người.
   - Phản hồi chính.
   - Sản phẩm đã sửa gì sau phản hồi.

8. **Giới hạn & bước tiếp theo**
   - Những gì MVP chưa làm.
   - Rủi ro hiện tại.
   - Hướng mở rộng.

---

## 4. Khi thuyết trình/demo cần làm gì?

- Demo theo **1 câu chuyện người dùng thật**, không nhảy màn hình lung tung.
- Mở đầu bằng **pain point**, không mở đầu bằng công nghệ.
- Chỉ nói công nghệ khi nó giải quyết một vấn đề cụ thể.
- Demo đủ chuỗi:
  - Nhập Requirement.
  - Tải dữ liệu.
  - AI hỏi làm rõ.
  - Sinh Data Model.
  - Xem ERD/DBML.
  - AI đề xuất sửa.
  - Accept/Reject.
  - Validation.
  - Sinh DDL.
  - Chạy Sandbox.
- Chủ động nói **1–2 giới hạn** của hệ thống.
- Khi bị hỏi “AI có đáng tin không?” → đưa **eval + Validation + Human Review**.
- Khi bị hỏi “tốt hơn làm thủ công ở đâu?” → đưa **số liệu trước–sau**.
- Khi bị hỏi “tại sao dùng AI?” → trả lời bằng phần cần hiểu ngôn ngữ nghiệp vụ và đề xuất mô hình; các bước xác định chắc chắn vẫn dùng code.
- Team phải cùng nắm: bài toán, kiến trúc, Agent, Validation, dữ liệu, giới hạn.

---

## 5. Kế hoạch làm nhanh theo thứ tự

1. **Chốt 1 kịch bản demo chuẩn.**
2. **Tạo bộ eval 20–50 case.**
3. **Chạy eval và lấy số liệu.**
4. **Phỏng vấn/test ≥5 người dùng hoặc chuyên gia.**
5. **Đo thời gian trước–sau khi dùng hệ thống.**
6. **Sửa UI theo phản hồi.**
7. **Test toàn bộ happy case + ca lỗi.**
8. **Deploy bản ổn định + tạo tài khoản demo.**
9. **Hoàn thiện README, CI, test report.**
10. **Làm slide bằng số liệu thật.**
11. **Tập demo và Q&A.**
12. **Chuẩn bị hồ sơ minh chứng: PR, task, họp, feedback, test, eval.**

---

## 6. 5 thứ đang thiếu đáng lo nhất

- **Chưa có số liệu eval cho AI.**
- **Chưa có nghiên cứu/test ≥5 người dùng.**
- **Chưa có số liệu chứng minh tiết kiệm thời gian hoặc giảm lỗi.**
- **Chưa có bộ minh chứng deploy/test/demo đủ rõ.**
- **Chưa có hồ sơ làm việc nhóm và phản hồi mentor → thay đổi sản phẩm.**
