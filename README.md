# 🤖 AI20K Agent System — DW Design & Requirement Automation

Hệ thống AI Agent tự động hóa phân tích yêu cầu (Requirement Analysis) và thiết kế mô hình kho dữ liệu (Data Warehouse Design), thuộc dự án **VinUni AI20K Build Phase - Cohort 4 (P-102)**.

Dự án được xây dựng theo chuẩn **Clean Architecture / DDD (Domain-Driven Design)**, tách biệt hoàn toàn giữa **Domain Layer**, **Application Layer**, **Infrastructure Layer** và **Presentation Layer**.

---

## 📐 Kiến trúc & Tech Stack

- **Tầng Domain & Application**: Python 3.13+, Dataclass Entities, Value Objects, Pure Business Invariants.
- **Tầng Infrastructure**: FastAPI, SQLAlchemy 2.0 (Async Engine + Mapped API), PostgreSQL 16.
- **Hệ thống AI Agent**: LangChain / LangGraph (Orchestrator Agent, Requirement Agent, DataSource Agent, DW Design Agent).
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
| **`OPENAI_API_KEY`** | `sk-...` | API Key kết nối với OpenAI LLMs. |
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

## 🔍 Truy cập API & Swagger UI Documentation

Sau khi backend khởi chạy thành công ở port **8001**, bạn có thể tương tác và kiểm thử API tại các đường dẫn sau:

- **Swagger UI (Interactive API Docs)**: [http://localhost:8001/docs](http://localhost:8001/docs)
- **ReDoc Documentation**: [http://localhost:8001/redoc](http://localhost:8001/redoc)
- **Health Check Endpoint**: [http://localhost:8001/health](http://localhost:8001/health)

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

#### Bằng `Python requests`:
```python
import requests

response = requests.get("http://localhost:8001/health")
print(response.status_code)  # 200
print(response.json())       # {'status': 'ok', 'env': 'development'}
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
│       │   ├── agents/                     # LLM Agent Implementations (Orchestrator, Requirement, DW Design)
│       │   ├── llm/                        # LLM Client Integrations (OpenAI, LangChain)
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
├── docs/                                   # 📖 Hướng dẫn Kỹ thuật & Sơ đồ Hệ thống
│   ├── guide_cho_ca_nhom/                  # Guidebook & Database Specifications
│   │   ├── database.md                     # Schema DBML chi tiết 10 bảng CSDL
│   │   ├── data_flow.md                    # Sơ đồ luồng dữ liệu & Agent Execution Flow
│   │   └── TECHNICAL_CODING_GUIDELINES.md  # Quy chuẩn lập trình bắt buộc
│   └── architecture_diagram.md
├── scripts/                                # 🔌 AI Logging Hooks & Helper Scripts
├── Dockerfile                              # Multi-stage Dockerfile cho Backend
├── docker-compose.yml                      # Docker Compose orchestrating PostgreSQL & Services
├── requirements.txt                        # Python Project Dependencies
├── ruff.toml                               # Ruff Linter Configuration
├── .env.example                            # Template biến môi trường
└── README.md                               # Document hướng dẫn dự án chính
```

---

## 📄 License & Liên Hệ

- **Dự án**: VinUni AI20K Build Phase — Cohort 4 (Nhóm P-102)
- **License**: Internal Educational & Research License.
