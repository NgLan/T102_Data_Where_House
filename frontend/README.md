🚀 AI Data Modeling Agent - Hướng Dẫn Phát Triển Frontend
Dự án này được xây dựng trên nền tảng Next.js (App Router), TypeScript, và Tailwind CSS v3. Hệ thống áp dụng kiến trúc Feature-Sliced Design (FSD) để phân tách mã nguồn theo từng cụm nghiệp vụ, giúp dự án dễ dàng mở rộng và bảo trì.

📌 1. Yêu Cầu Môi Trường
Node.js: Phiên bản v20.x hoặc v22.x (Ví dụ: v22.12.0).

Trình quản lý gói: npm.

🛠 2. Cài Đặt & Khởi Chạy
Mở terminal tại thư mục frontend và chạy các lệnh sau:

Bash
# Cài đặt các thư viện phụ thuộc
npm install

# Khởi chạy môi trường phát triển ở localhost:3000
npm run dev
📂 3. Kiến Trúc Thư Mục (FSD Pattern)
Toàn bộ logic của ứng dụng nằm trong thư mục src/, được chia thành 4 phân vùng chính:

src/api/: Tầng cấu hình giao tiếp dữ liệu gốc (Axios instances, Types/Models dùng chung cho API).

src/app/: Tầng định tuyến (Routing) theo chuẩn App Router của Next.js. Chứa các file page.tsx, layout.tsx.

src/common/: Tầng tài nguyên dùng chung. Bao gồm UI components (shadcn/ui), global hooks, utils và global stores không thuộc về một nghiệp vụ cụ thể nào.

src/features/: Tầng nghiệp vụ cốt lõi. Đây là nơi chứa logic chính của ứng dụng, được chia thành 4 module độc lập theo tài liệu PRD:

project-init/: Giao diện khởi tạo dự án, upload DDL và nhập ngữ cảnh nghiệp vụ.

modeling-dashboard/: Bảng điều khiển mô hình hóa, render sơ đồ ERD (Mermaid.js) và quản lý Fact/Dim.

hitl-editor/: Giao diện tinh chỉnh Human-in-the-loop, bảng data-grid và khung chat tương tác với LLM.

sandbox-deployment/: Môi trường thử nghiệm, xuất code SQL DDL và xem log thực thi.

📝 4. Quy Ước Code (Coding Conventions)
Nguyên tắc Đóng Gói Nghệp Vụ (Colocation): Tính năng nào thì code nằm gọn trong thư mục của tính năng đó (src/features/...). KHÔNG gọi chéo logic nội bộ giữa các features với nhau. Nếu một component cần dùng ở nhiều features, hãy chuyển nó sang src/common/.

Bắt Buộc Comment Code: Luôn phải có comment giải thích ngắn gọn bằng tiếng Việt phía trên các function hoặc custom hooks được tạo ra để các thành viên khác dễ dàng nắm bắt logic.

Styling: Sử dụng hoàn toàn Tailwind CSS v3 thông qua class name. Các class động nên được xử lý qua hàm tiện ích (ví dụ: cn()).