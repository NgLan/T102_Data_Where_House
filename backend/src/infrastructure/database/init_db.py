"""Khởi tạo schema SQLAlchemy trong môi trường development."""

import asyncio

from config import Settings, get_settings
from src.common.logging import get_logger
from src.infrastructure.database import models as _models  # noqa: F401
from src.infrastructure.database.base import Base
from src.infrastructure.database.config import get_async_db_engine
from src.infrastructure.database.error_translation import translate_database_errors

logger = get_logger(__name__)


@translate_database_errors
async def init_db(settings: Settings | None = None) -> None:
    """Tạo các bảng development; production dùng migration tiến tới.

    Args:
        settings: Cấu hình được inject cho startup hoặc test.

    Raises:
        InfrastructureException: Khi SQLAlchemy không thể tạo schema.
    """
    app_settings = settings or get_settings()
    if app_settings.app_env != "development":
        logger.info("database_schema_sync_skipped environment=%s", app_settings.app_env)
        return
    async with get_async_db_engine().begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    logger.info("database_schema_sync_completed")


if __name__ == "__main__":
    asyncio.run(init_db())
