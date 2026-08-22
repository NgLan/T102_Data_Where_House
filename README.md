# 🤖 AI20K Agent System — DW Design & Requirement Automation

Hệ thống AI Agent tự động hóa phân tích yêu cầu (Requirement Analysis) và thiết kế mô hình kho dữ liệu (Data Warehouse Design), thuộc dự án **VinUni AI20K Build Phase - Cohort 4 (P-102)**.

Dự án được xây dựng theo chuẩn **Clean Architecture / DDD (Domain-Driven Design)**, tách biệt hoàn toàn giữa **Domain Layer**, **Application Layer**, **Infrastructure Layer** và **Presentation Layer**.

---

## 📐 Kiến trúc & Tech Stack

- **Tầng Domain & Application**: Python 3.13+, Dataclass Entities, Value Objects, Pure Business Invariants.
- **Tầng Infrastructure**: FastAPI, SQLAlchemy 2.0 (Async Engine + Mapped API), PostgreSQL 16.
- **Hệ thống AI**: LangChain với workflow tuần tự tại Application; RequirementAgent và DWDesignAgent độc lập provider, mỗi operation gọi LLM đúng một lần.
- **Containerization & DevOps**: Docker, Docker Compose, Pytest, Ruff Linter.

---

## ⚙️ Yêu cầu tiền đề (Prerequisites)

Tùy thuộc vào hệ điều hành của bạn (Windows, Linux, macOS), hãy chuẩn bị các công cụ sau:

- **Python**: phiên bản `>= 3.11` (khuyên dùng Python 3.13).
- **Docker & Docker Compose**: phiên bản v2.0+.
- **Git**: dùng để quản lý mã nguồn.

---

## 🚀 Hướng dẫn Setup & Khởi chạy Chi tiết (Step-by-Step)

### Bước 1: Clone Repository & Tạo Virtual Environment

```bash
# Clone repository về máy local
git clone https://github.com/AI20K-Build-Phase-Cohort-3/P-102.git
cd P-102

# Tạo môi trường ảo virtualenv (Python)
python -m venv .venv

# Kích hoạt môi trường ảo:
# Trên Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# Trên Linux / macOS / Git Bash:
source .venv/bin/activate
```

---

### Bước 2: Cài đặt Dependencies

```bash
# Cập nhật pip và cài đặt các thư viện cần thiết
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Bước 3: Cấu hình Biến Môi Trường (`.env`)

Sao chép file mẫu `.env.example` thành `.env` và thiết lập cấu hình:

```bash
# Linux / macOS / Git Bash
cp .env.example .env

# Windows PowerShell
copy .env.example .env
```

#### 🔑 Giải thích chi tiết các biến môi trường quan trọng trong `.env`:

| Biến môi trường | Giá trị mặc định | Mô tả chi tiết |
| :--- | :--- | :--- |
| **`APP_NAME`** | `"AI20K Agent System"` | Tên đại diện ứng dụng. |
| **`APP_ENV`** | `development` | Môi trường chạy (`development`, `staging`, `production`). |
| **`APP_HOST`** | `0.0.0.0` | Host bind ứng dụng FastAPI. |
| **`APP_PORT`** | `8001` | **Port chạy của Backend Server (8001)**. |
| **`POSTGRES_USER`** | `postgres` | Tài khoản quản trị PostgreSQL. |
| **`POSTGRES_PASSWORD`** | `postgres` | Mật khẩu truy cập PostgreSQL. |
| **`POSTGRES_HOST`** | `localhost` / `127.0.0.1` | Địa chỉ host của CSDL PostgreSQL. |
| **`POSTGRES_PORT`** | `5432` / `5434` | Port lắng nghe kết nối CSDL PostgreSQL. |
| **`POSTGRES_DB`** | `ai20k_db` | Tên cơ sở dữ liệu chính. |
| **`DATABASE_URL`** | `postgresql+asyncpg://...` | Chuỗi kết nối Async Engine cho SQLAlchemy. |
| **`LLM_PROVIDER`** | `openai` | Provider: `openai`, `openai_compatible` hoặc `google`. |
| **`LLM_API_KEY`** | trống | API key dùng chung; có fallback sang biến provider cũ. |
| **`LLM_BASE_URL`** | trống | Base URL cho OpenAI-compatible/OpenRouter/local. |
| **`MODEL_NAME`** | provider default | Tên model dùng cho Agent operation. |
| **`LOG_LEVEL`** | `INFO` | Mức độ ghi log hệ thống (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |

---

### Bước 4: Khởi chạy PostgreSQL Database bằng Docker

Sử dụng Docker Compose để khởi chạy dịch vụ PostgreSQL 16 containerized:

```bash
# Khởi chạy duy nhất container PostgreSQL ở chế độ background (-d)
docker compose up -d postgres

# Kiểm tra trạng thái container đang hoạt động
docker compose ps

# (Tùy chọn) Xem logs của container database
docker compose logs -f postgres

# Dừng container PostgreSQL khi không sử dụng
docker compose down

# (Tùy chọn) Dừng container và xóa toàn bộ dữ liệu volume nếu muốn reset lại từ đầu
docker compose down -v
```

> 💡 **Lưu ý:** Container PostgreSQL sẽ tạo một volume persistent `postgres_data` để lưu trữ dữ liệu bền vững ngay cả khi stop container. Khi muốn xóa toàn bộ dữ liệu để khởi tạo lại CSDL sạch, bạn có thể dùng `docker compose down -v`.

---

### Bước 5: Khởi chạy Backend FastAPI Server ở Port 8001

Khởi chạy server Uvicorn bất đồng bộ trên Cổng **8001**:

```bash
# Cách 1: Chạy từ thư mục backend
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Cách 2: Chạy trực tiếp từ thư mục gốc dự án P-102
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
```

Màn hình Terminal thông báo thành công:
```text
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

---

### Bước 6: Khởi chạy Giao diện Frontend Web ở Port 3000

Mở một cửa sổ Terminal mới để khởi chạy ứng dụng Frontend (Next.js / React / TypeScript):

```bash
# Di chuyển vào thư mục frontend và cài đặt dependencies
cd frontend
npm install

# Khởi chạy Next.js development server
npm run dev
```

Sau khi khởi chạy thành công, mở trình duyệt web và truy cập giao diện tại:
👉 **[http://localhost:3000](http://localhost:3000)**

---

## 🔍 Truy cập API & Swagger UI Documentation

Sau khi backend khởi chạy thành công ở port **8001**, bạn có thể tương tác và kiểm thử API tại các đường dẫn sau:

- **Swagger UI (Interactive API Docs)**: [http://localhost:8001/docs](http://localhost:8001/docs)
- **ReDoc Documentation**: [http://localhost:8001/redoc](http://localhost:8001/redoc)
- **Health Check Endpoint**: [http://localhost:8001/health](http://localhost:8001/health)

---

## 🎯 Dữ Liệu Mẫu & Kịch Bản Kiểm Thử Cho Mentor (Sample Data & Test Scenarios)

Dự án cung cấp sẵn bộ dữ liệu mẫu thực tế của **Bài toán Quản lý & Lưu trữ Hồ sơ Bệnh án (Y tế)** để Mentor và người đánh giá có thể chạy thử nghiệm ngay trên giao diện web mà không cần tự chuẩn bị:

### 1. Dữ Liệu Đầu Vào (Input Data Form)

- **Văn bản Yêu cầu Nghiệp vụ (Requirement Text)**:
  *(Copy trực tiếp đoạn văn bản dưới đây hoặc lấy từ tệp [`eval/sample/YeuCauNghiepVuYTe.md`](eval/sample/YeuCauNghiepVuYTe.md) dán vào ô nhập Requirement trên màn hình khởi tạo dự án)*

  > "Bệnh viện cần xây dựng Kho dữ liệu (Data Warehouse) để quản lý và phân tích hồ sơ bệnh án lưu trữ, phục vụ các mục tiêu sau:
  > 1. Phân tích tình hình khám chữa bệnh: Theo dõi số lượng bệnh nhân, thời gian điều trị trung bình (tính từ thời gian vào viện đến ngày ra viện) phân theo từng khoa phòng (vào từ khoa nào, ra từ khoa nào), nhóm tuổi và giới tính.
  > 2. Quản lý đối tượng bệnh nhân: Thống kê cơ cấu bệnh nhân theo diện chi trả (BHYT, BHYT Quân, Miễn phí, Dịch vụ) và loại hình điều trị (Nội trú, Ngoại trú).
  > 3. Tối ưu hóa công tác lưu trữ hồ sơ: Quản lý vị trí vật lý lưu trữ hồ sơ bệnh án (theo Kho, Tủ, Ngăn, Kệ, Ký hiệu) và trạng thái hồ sơ (đang lưu trữ, chờ đưa vào kho, cần bổ sung xét nghiệm) để phục vụ tra cứu nhanh chóng và bảo mật thông tin cá nhân của bệnh nhân."

- **4 Tệp Dữ Liệu Nguồn CSV Thực Tế (Source Data)**:
  *(Kéo thả trực tiếp 4 tệp có sẵn trong thư mục `eval/sample/` vào Upload Zone)*
  - [`eval/sample/DanhSachBenhNhan.csv`](eval/sample/DanhSachBenhNhan.csv)
  - [`eval/sample/ThongTinBenhNhan.csv`](eval/sample/ThongTinBenhNhan.csv)
  - [`eval/sample/ThongtinHoSoLuuTru.csv`](eval/sample/ThongtinHoSoLuuTru.csv)
  - [`eval/sample/DanhSachHoSoLuuTru.csv`](eval/sample/DanhSachHoSoLuuTru.csv)

---

### 2. Kịch Bản Tinh Chỉnh Mô Hình Human-in-the-Loop (HITL Re-prompt)

Sau khi workflow tuần tự hoàn tất phân tích và sinh mô hình DBML đầu tiên, Mentor có thể thử nghiệm tính năng tinh chỉnh bằng ngôn ngữ tự nhiên tại khung **AI Re-prompt**:

- **Câu lệnh mẫu 1 (Tách bảng Dimension Chẩn đoán)**:
  > "Trong mô hình vừa sinh, hãy tách riêng thông tin chẩn đoán bệnh (chẩn đoán vào viện, chẩn đoán ra viện) thành một bảng Dimension chẩn đoán riêng biệt (gồm mã định danh, tên chẩn đoán, nhóm bệnh) và liên kết khóa ngoại với bảng Fact chứa thông tin hồ sơ/khám chữa bệnh."

- **Câu lệnh mẫu 2 (Bổ sung thuộc tính & Bảng vị trí lưu trữ)**:
  > "Hãy bổ sung thêm trường `so_ngay_dieu_tri` vào bảng Fact và tạo bảng `Dim_KhoLuuTru` để quản lý thông tin kho, tủ, ngăn, kệ."

*Sau khi gửi lệnh, hệ thống sẽ sinh ra bản ghi đề xuất thay đổi (`data_model_changes`) kèm hiển thị so sánh phiên bản (Diff). Mentor có thể nhấn nút **Accept** để áp dụng hoặc **Reject** để giữ nguyên mô hình.*

---

## 💡 Sample Queries & HTTP Requests (Ví dụ Gọi API)

### 1. Health Check Query

#### Bằng `cURL`:
```bash
curl -X GET "http://localhost:8001/health" -H "accept: application/json"
```

#### Kết quả trả về (Response):
```json
{
  "status": "ok",
  "env": "development"
}
```

---

### 2. Kiểm tra Kết nối Database qua Python Script mẫu

Tạo một script nhỏ hoặc chạy trong `python` REPL để kiểm tra Async Engine kết nối tới Database Docker:

```python
import asyncio
from backend.src.infrastructure.database.session import AsyncSessionFactory
from sqlalchemy import text

async def test_db_connection():
    async with AsyncSessionFactory() as session:
        result = await session.execute(text("SELECT 1;"))
        print("Database Connection Success:", result.scalar() == 1)

asyncio.run(test_db_connection())
```

---

## 🧪 Kiểm thử (Testing) & Linter Code Quality

Dự án tích hợp sẵn bộ kiểm thử đơn vị (Unit tests) bao phủ Domain Entities, Mappers, và Repositories.

### Chạy Unit Test Suite (Pytest)

```bash
# Chạy tất cả test suites
python -m pytest tests/ -v

# Chạy cụ thể các bài test domain, database models, mappers và repositories
python -m pytest tests/test_domain.py tests/test_database_models.py tests/test_mappers.py tests/test_repositories.py -v
```

### Kiểm tra Mã nguồn với Ruff Linter

```bash
# Kiểm tra các lỗi linter và chuẩn format mã nguồn
python -m ruff check backend/src/ tests/

# Tự động sửa các lỗi cơ bản
python -m ruff check --fix backend/src/ tests/
```

---

## 📂 Cấu trúc Thư mục Dự án (Full Clean Architecture Structure)

```text
P-102/
├── backend/                                # Backend Module chính (Python / FastAPI)
│   ├── config.py                           # Cấu hình Pydantic Settings từ .env
│   ├── main.py                             # FastAPI Entrypoint (chạy Uvicorn ở Port 8001)
│   └── src/
│       ├── presentation/                   # 🌐 Tầng Presentation (API Endpoints, Schemas, Router)
│       │   ├── api/
│       │   │   ├── router.py               # Root API Router
│       │   │   └── v1/                     # API Routers Version 1
│       │   │       ├── auth.py             # Auth & Identity Endpoints
│       │   │       ├── users.py            # User Management Endpoints
│       │   │       ├── projects.py         # Project Management Endpoints
│       │   │       ├── requirements.py     # Requirements Management Endpoints
│       │   │       ├── analytical_requirements.py # Analytical Requirements Endpoints
│       │   │       ├── data_sources.py     # Data Source Integration Endpoints
│       │   │       ├── sessions.py         # Agent Sessions & Event Endpoints
│       │   │       ├── data_models.py      # Data Models & DBML Endpoints
│       │   │       ├── data_model_changes.py # Proposed Changes Endpoints
│       │   │       └── workflows.py        # AI Agent Workflow Execution Endpoints
│       │   ├── dependencies/               # Dependency Injection cho FastAPI Routes
│       │   ├── exception_handlers/         # HTTP Exception Translators
│       │   ├── middleware/                 # CORS, Security Headers, Logging Middlewares
│       │   └── schemas/                    # Pydantic Schemas cho API Request/Response DTOs
│       │
│       ├── application/                    # ⚙️ Tầng Application (Use Cases, Application Services)
│       │   ├── auth/                       # Authentication Use Cases
│       │   ├── projects/                   # Project Use Cases
│       │   ├── requirements/               # Requirement Processing Use Cases
│       │   ├── analytical_requirements/    # Analytical Requirement Extraction Use Cases
│       │   ├── data_sources/               # Data Source Profiling Use Cases
│       │   ├── data_models/                # DW Design & Revision Use Cases
│       │   ├── sessions/                   # Agent Session Management Use Cases
│       │   ├── workflows/                  # Agent Workflow Execution & Orchestration Services
│       │   └── common/                     # Common Application DTOs & Interfaces
│       │
│       ├── domain/                         # 🧠 Tầng Domain (Pure Entities, Value Objects, Enums, Rules)
│       │   ├── user/                       # User Entity, Email VO, UserRepository Interface
│       │   ├── project/                    # Project Entity, Member Entity, Roles, Enums
│       │   ├── requirement/                # Requirement Entity, Priority & Type Enums
│       │   ├── analytical_requirement/     # Analytical Requirement Entity, Aggregation Enum
│       │   ├── data_source/                # DataSource Entity, SchemaMetadata VO, Column/Table VO
│       │   ├── project_session/            # ProjectSession & SessionEvent Entities, Event Metadata VOs
│       │   ├── data_model/                 # DataModel & DataModelChange Entities
│       │   └── shared/                     # BaseEntity, BaseValueObject, EntityID, IBaseRepository
│       │
│       ├── infrastructure/                 # 🛠️ Tầng Infrastructure (Database, LLMs, Agents, Cache)
│       │   ├── database/
│       │   │   ├── base.py                 # Base Declarative Class (Domain Timestamps)
│       │   │   ├── config.py               # AsyncEngine & Database URLs
│       │   │   ├── constants.py            # Hằng số giới hạn độ dài trường CSDL
│       │   │   ├── mappers/                # Domain ↔ Persistence Mappers (10 mappers)
│       │   │   ├── models/                 # SQLAlchemy 2.0 ORM Models (10 tables)
│       │   │   └── session.py              # AsyncSession Generator & Connection Management
│       │   ├── repositories/               # PostgreSQL Repository Implementations (10 repos)
│       │   ├── agents/                     # Requirement/DW Design adapters và DBML validation
│       │   ├── llm/                        # Provider registry, lazy model và structured invoker
│       │   ├── cache/                      # Redis Cache Implementations
│       │   ├── security/                   # Password Hashing & JWT Handlers
│       │   ├── storage/                    # File & Schema Storage
│       │   ├── transaction/                # Unit of Work / Transaction Management
│       │   └── observability/              # LangSmith & Logging Integrations
│       │
│       └── common/                         # 🔧 Shared Cross-Cutting Concerns
│           ├── dto/                        # ApiResponse DTOs & Standard Envelopes
│           ├── exceptions/                 # System, Domain, Infrastructure Exception Hierarchy
│           ├── logging/                    # Centralized Structured Logging Configuration
│           ├── middleware/                 # Request ID, HTTP Logging, Security Middlewares
│           ├── utils/                      # Datetime & String Utilities
│           └── constants/                  # System-wide Constants
│
├── frontend/                               # 🖥️ Frontend Web Application (Next.js / React)
├── tests/                                  # 🧪 Pytest Test Suites (Domain, Models, Mappers, Repos)
│   ├── test_domain.py                      # Tests kiểm thử Domain Entities & Business Rules
│   ├── test_database_models.py             # Tests kiểm thử SQLAlchemy ORM Mapping
│   ├── test_mappers.py                     # Tests kiểm thử Domain ↔ Persistence Mappers
│   └── test_repositories.py                # Tests kiểm thử Async Repositories
├── eval/                                   # 🧪 Dữ liệu Mẫu & Báo cáo Đánh giá (Evaluation)
│   ├── sample/                             # Dữ liệu mẫu thực tế (4 file CSV Y tế & Requirement text)
│   │   ├── YeuCauNghiepVuYTe.md            # Toàn văn yêu cầu nghiệp vụ Y tế mẫu
│   │   ├── DanhSachBenhNhan.csv            # File CSV nguồn 1: Danh sách bệnh nhân
│   │   ├── ThongTinBenhNhan.csv            # File CSV nguồn 2: Chi tiết thông tin bệnh nhân
│   │   ├── ThongtinHoSoLuuTru.csv          # File CSV nguồn 3: Chi tiết hồ sơ lưu trữ
│   │   └── DanhSachHoSoLuuTru.csv          # File CSV nguồn 4: Danh mục hồ sơ lưu trữ
│   └── results/                            # Báo cáo đánh giá chất lượng
│       └── report.md                       # Báo cáo 5 Test Cases thực tế
├── scripts/                                # 🔌 AI Logging Hooks & Helper Scripts
├── Dockerfile                              # Multi-stage Dockerfile cho Backend
├── docker-compose.yml                      # Docker Compose orchestrating PostgreSQL & Services
├── requirements.txt                        # Python Project Dependencies
├── ruff.toml                               # Ruff Linter Configuration
├── .env.example                            # Template biến môi trường
├── ARCHITECTURE.md                         # Sơ đồ kiến trúc & luồng dữ liệu hệ thống
└── README.md                               # Document hướng dẫn dự án chính
```

---

## 📄 License & Liên Hệ

- **Dự án**: VinUni AI20K Build Phase — Cohort 4 (Nhóm P-102)
- **License**: Internal Educational & Research License.
