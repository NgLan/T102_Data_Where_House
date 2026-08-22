"""Cấu hình khởi tạo và quản lý kết nối CSDL PostgreSQL (Engine & Database URLs)."""

from functools import lru_cache

from config import Settings, get_settings
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def get_async_database_url(settings: Settings | None = None) -> str:
    """Tạo chuỗi URL kết nối bất đồng bộ PostgreSQL (postgresql+asyncpg://)."""
    app_settings: Settings = settings or get_settings()
    if app_settings.database_url and "asyncpg" in app_settings.database_url:
        return app_settings.database_url
    if app_settings.database_url and app_settings.database_url.startswith("postgresql://"):
        return app_settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
    return (
        f"postgresql+asyncpg://{app_settings.postgres_user}:{app_settings.postgres_password}"
        f"@{app_settings.postgres_host}:{app_settings.postgres_port}/{app_settings.postgres_db}"
    )


@lru_cache
def get_async_db_engine() -> AsyncEngine:
    """Tạo hoặc lấy AsyncEngine kết nối bất đồng bộ PostgreSQL."""
    app_settings = get_settings()
    url: str = get_async_database_url(app_settings)
    return create_async_engine(
        url,
        echo=app_settings.database_echo,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )


async def dispose_async_db_engine() -> None:
    """Đóng connection pool và xóa engine đã cache."""
    if get_async_db_engine.cache_info().currsize:
        await get_async_db_engine().dispose()
        get_async_db_engine.cache_clear()
