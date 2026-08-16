"""Điểm đầu vào chính (Entrypoint) khởi tạo ứng dụng FastAPI."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from config import Settings, get_settings
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from src.common.exceptions import register_exception_handlers
from src.common.logging import configure_logging, get_logger
from src.common.middleware import (
    HTTPLoggingMiddleware,
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
    setup_cors_middleware,
)
from src.infrastructure.database.init_db import init_db
from src.presentation.api.router import router as api_router
from src.presentation.dtos.common import ApiErrorResponse
from src.presentation.dtos.health import HealthResponse
from src.presentation.routing import ApiResponseRoute

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Quản lý vòng đời khởi chạy và dừng ứng dụng."""
    settings: Settings = get_settings()
    logger.info("Starting %s in %s mode", settings.app_name, settings.app_env)

    # 1. Gọi hàm init_db() để khởi tạo CSDL
    try:
        await init_db(settings)
    except Exception as exc:
        logger.warning("Không thể khởi tạo CSDL lúc startup: %s", exc)

    yield
    logger.info("Shutting down application...")


def create_app() -> FastAPI:
    """Khởi tạo và cấu hình ứng dụng FastAPI."""
    settings: Settings = get_settings()

    # 1. Cấu hình hệ thống Logging tập trung toàn dự án
    configure_logging(settings)

    app: FastAPI = FastAPI(
        title=settings.app_name,
        description="AI20K Agent System API",
        version="1.0.0",
        debug=settings.debug,
        lifespan=lifespan,
    )
    app.router.route_class = ApiResponseRoute

    # 2. Đăng ký Middleware Layer theo thứ tự thực thi (Innermost -> Outermost)
    # Innermost: HTTP Logging Middleware (Ghi nhận duration và log request lifecycle)
    app.add_middleware(HTTPLoggingMiddleware)

    # Context: Request ID Middleware (Thiết lập ContextVar và X-Request-ID response header)
    app.add_middleware(RequestIDMiddleware)

    # CORS Middleware Configuration
    setup_cors_middleware(app, settings)

    # Outermost: Security Headers Middleware (Bổ sung Security Headers)
    if settings.security_headers_enabled:
        app.add_middleware(
            SecurityHeadersMiddleware,
            enable_hsts=settings.security_hsts_enabled,
        )

    # Trusted Host Validation (Nếu được kích hoạt)
    if settings.trusted_host_enabled:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts_list,
        )

    # 3. Đăng ký hệ thống xử lý ngoại lệ tập trung (Global Exception Handlers)
    register_exception_handlers(app)
    app.include_router(api_router)

    @app.get(
        "/health",
        tags=["Health Check"],
        response_model=HealthResponse,
        operation_id="healthCheck",
        responses={500: {"model": ApiErrorResponse}},
    )
    async def health_check() -> HealthResponse:
        """Endpoint kiểm tra trạng thái hoạt động của hệ thống."""
        return HealthResponse(status="ok", env=settings.app_env)

    return app


app: FastAPI = create_app()

if __name__ == "__main__":
    import uvicorn

    settings_env: Settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings_env.app_host,
        port=settings_env.app_port,
        reload=(settings_env.app_env == "development"),
    )
