"""Cấu hình tập trung toàn bộ hệ thống (App, DB, Redis, Security, LLM, Agent, Observability, CORS)."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Cấu hình tập trung quản lý các biến môi trường cho ứng dụng."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # =========================================================================
    # 1. Application Configuration
    # =========================================================================
    app_name: str
    app_env: Literal["development", "production", "test"]
    app_host: str
    app_port: int = Field(ge=1, le=65535)
    debug: bool

    # =========================================================================
    # 2. Database Configuration (PostgreSQL)
    # =========================================================================
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int = Field(ge=1, le=65535)
    postgres_db: str
    database_url: str = ""

    # =========================================================================
    # 3. Redis Configuration (Cache & Session)
    # =========================================================================
    redis_host: str
    redis_port: int = Field(ge=1, le=65535)
    redis_password: str = ""
    redis_db: int = Field(ge=0)

    # =========================================================================
    # 4. Security Configuration (JWT & Auth)
    # =========================================================================
    secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int = Field(ge=1)

    # =========================================================================
    # 5. LLM Configuration (OpenAI / Language Models)
    # =========================================================================
    openai_api_key: str = ""
    model_name: str
    llm_temperature: float = Field(ge=0.0, le=2.0)
    max_tokens: int = Field(ge=1)
<<<<<<< HEAD
=======
    # Thời gian chờ tối đa một lời gọi LLM (giây) — NFR2 giới hạn 45 giây cho cả pipeline
>>>>>>> d3fd3dc (feat(agents): Fix agents)
    llm_request_timeout_seconds: float = Field(default=60.0, gt=0)

    # =========================================================================
    # 6. Agent Configuration (LangGraph & Vector Store)
    # =========================================================================
    agent_max_iterations: int = Field(ge=1)
    chroma_persist_dir: str
    enable_human_in_the_loop: bool
    # Che thông tin cá nhân trước khi gửi dữ liệu sang LLM API (FR6.2).
    # Mặc định luôn BẬT; chỉ tắt khi cần gỡ lỗi chất lượng đầu ra của Agent.
    pii_masking_enabled: bool = Field(default=True)

    # =========================================================================
    # 7. Observability Configuration (Logging & Tracing)
    # =========================================================================
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]
    log_format: Literal["console", "json"] = "console"
    log_request_body: bool = False
    langchain_tracing_v2: bool
    langchain_api_key: str = ""
    langchain_project: str

    # =========================================================================
    # 8. CORS & Middleware Configuration
    # =========================================================================
    cors_origins: str
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
    cors_allow_headers: str = "*"

    request_id_header: str = "X-Request-ID"
    security_headers_enabled: bool = True
    security_hsts_enabled: bool = False
    trusted_host_enabled: bool = False
    allowed_hosts: str = "localhost,127.0.0.1"

    # -------------------------------------------------------------------------
    # Helper Properties
    # -------------------------------------------------------------------------
    @property
    def async_database_url(self) -> str:
        """Trả về URL kết nối bất đồng bộ đến PostgreSQL."""
        from src.infrastructure.database.config import get_async_database_url

        return get_async_database_url(self)

    @property
    def sync_database_url(self) -> str:
        """Trả về URL kết nối đồng bộ đến PostgreSQL."""
        from src.infrastructure.database.config import get_sync_database_url

        return get_sync_database_url(self)

    @property
    def redis_url(self) -> str:
        """Trả về URL kết nối đến Redis."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def cors_origins_list(self) -> list[str]:
        """Trả về danh sách origins được phép truy cập CORS."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def cors_allow_methods_list(self) -> list[str]:
        """Trả về danh sách HTTP Methods cho phép CORS."""
        return [method.strip() for method in self.cors_allow_methods.split(",") if method.strip()]

    @property
    def cors_allow_headers_list(self) -> list[str]:
        """Trả về danh sách HTTP Headers cho phép CORS."""
        return [header.strip() for header in self.cors_allow_headers.split(",") if header.strip()]

    @property
    def allowed_hosts_list(self) -> list[str]:
        """Trả về danh sách Trusted Hosts."""
        return [host.strip() for host in self.allowed_hosts.split(",") if host.strip()]


@lru_cache
def get_settings() -> Settings:
    """Khởi tạo và lưu cache cấu hình hệ thống."""
    return Settings()

