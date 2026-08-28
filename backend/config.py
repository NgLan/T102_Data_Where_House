"""Cấu hình tập trung toàn bộ hệ thống (App, DB, Redis, Security, LLM, Agent, Observability, CORS)."""

from functools import lru_cache
from pathlib import Path
from typing import Literal
from uuid import UUID

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from src.infrastructure.llm.settings_types import SecretListSetting, StringListSetting


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
    database_echo: bool = False

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
    mvp_actor_id: UUID = UUID("a678ac27-3077-5ef2-8919-5218b2e48791")
    mvp_actor_username: str = "annv"
    mvp_actor_email: str = "an.nguyen@dataworks.vn"
    upload_dir: Path = Path("data/uploads")

    # =========================================================================
    # 5. LLM Configuration
    # =========================================================================
    openai_api_key: str = ""
    openai_base_url: str = ""
    google_api_key: str = ""
    llm_provider: str = ""
    llm_provider_priority: StringListSetting = ()
    llm_api_keys: SecretListSetting | None = None
    llm_api_key: str = ""
    llm_base_url: str = ""
    model_name: str = ""
    gemini_api_keys: SecretListSetting = ()
    openai_api_keys: SecretListSetting = ()
    anthropic_api_keys: SecretListSetting = ()
    gemini_model: str = ""
    openai_model: str = ""
    anthropic_model: str = ""
    gemini_summary_model: str = ""
    openai_summary_model: str = ""
    anthropic_summary_model: str = ""
    anthropic_base_url: str = ""
    llm_temperature: float = Field(ge=0.0, le=2.0)
    # Thời gian chờ tối đa một lời gọi LLM (giây) — NFR2 giới hạn 45 giây cho cả pipeline
    llm_request_timeout_seconds: float = Field(default=60.0, gt=0)
    llm_credential_cooldown_seconds: float = Field(default=60.0, gt=0)
    llm_provider_failure_threshold: int = Field(default=2, ge=1)
    llm_provider_cooldown_seconds: float = Field(default=30.0, gt=0)

    # =========================================================================
    # 6. Agent Configuration
    # =========================================================================
    # Trần token đầu ra: các operation thiết kế phải xuất trọn một schema
    # dạng JSON/DBML: chạm trần giữa chừng là structured output vỡ và cả pipeline hỏng
    # với lỗi `LengthFinishReasonError`.
    agent_max_output_tokens: int = Field(default=8000, ge=1024)
    structured_output_max_attempts: int = Field(default=3, ge=1, le=5)
    conversation_context_window_tokens: int = Field(default=32768, ge=4096)
    conversation_recent_turns: int = Field(default=6, ge=1)
    conversation_summary_batch_size: int = Field(default=4, ge=1)
    conversation_token_chars_per_token: float = Field(default=4.0, gt=0)
    conversation_project_context_soft_target: float = Field(default=0.45, ge=0.0, le=1.0)
    conversation_summary_soft_target: float = Field(default=0.10, ge=0.0, le=1.0)
    conversation_history_soft_target: float = Field(default=0.20, ge=0.0, le=1.0)
    conversation_summary_model_name: str = ""
    conversation_summary_temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    conversation_summary_max_output_tokens: int = Field(default=1500, ge=256)
    # Che thông tin cá nhân trước khi gửi dữ liệu sang LLM API (FR6.2).
    # Mặc định luôn BẬT; chỉ tắt khi cần gỡ lỗi chất lượng đầu ra của Agent.
    pii_masking_enabled: bool = Field(default=True)
    pii_default_language: str = "vi"
    pii_supported_languages: str = "vi,en,ja"
    pii_score_threshold: float = Field(default=0.4, ge=0.0, le=1.0)

    @field_validator("llm_api_keys")
    @classmethod
    def validate_llm_api_keys(
        cls, keys: tuple[SecretStr, ...] | None
    ) -> tuple[SecretStr, ...] | None:
        """Chuẩn hóa key list mới và từ chối cấu hình rỗng hoặc trùng."""
        if keys is None:
            return None
        normalized = tuple(SecretStr(key.get_secret_value().strip()) for key in keys)
        values = tuple(key.get_secret_value() for key in normalized)
        if not values or any(not value for value in values):
            raise ValueError("LLM_API_KEYS phải chứa ít nhất một key không rỗng.")
        if len(set(values)) != len(values):
            raise ValueError("LLM_API_KEYS không được chứa key trùng nhau.")
        return normalized

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

    @property
    def pii_supported_languages_list(self) -> tuple[str, ...]:
        """Trả các language code được PII analyzer hỗ trợ."""
        return tuple(
            language.strip()
            for language in self.pii_supported_languages.split(",")
            if language.strip()
        )


@lru_cache
def get_settings() -> Settings:
    """Khởi tạo và lưu cache cấu hình hệ thống."""
    return Settings()
