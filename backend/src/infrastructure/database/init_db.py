"""Script tự động kiểm tra và khởi tạo các bảng CSDL cho hệ thống."""

import asyncio

from config import Settings, get_settings
from src.common.logging import get_logger
from src.infrastructure.database.base import Base
from src.infrastructure.database.config import get_async_db_engine

logger = get_logger(__name__)


async def init_db(settings: Settings | None = None) -> None:
    """Kiểm tra và tự động khởi tạo/cập nhật cấu trúc bảng CSDL nếu ở môi trường development."""
    app_settings = settings or get_settings()

    if app_settings.app_env != "development":
        logger.info("Bỏ qua tự động sync schema CSDL ở môi trường %s", app_settings.app_env)
        return

    logger.info("Kiểm tra kết nối CSDL và đồng bộ schema các bảng ở môi trường development...")
    engine = get_async_db_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("CSDL đã được khởi tạo và đồng bộ bảng thành công!")


if __name__ == "__main__":
    asyncio.run(init_db())
