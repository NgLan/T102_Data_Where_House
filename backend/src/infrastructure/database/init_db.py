"""Script tự động kiểm tra và khởi tạo các bảng CSDL cùng Default User cho hệ thống."""

import asyncio

from config import Settings, get_settings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.logging import get_logger
from src.infrastructure.database.base import Base
from src.infrastructure.database.config import get_async_db_engine
from src.infrastructure.database.constants import (
    DEFAULT_USER_EMAIL,
    DEFAULT_USER_ID,
    DEFAULT_USER_NAME,
)
from src.infrastructure.database.models.user import UserModel

logger = get_logger(__name__)


async def init_db(settings: Settings | None = None) -> None:
    """Kiểm tra và tự động khởi tạo/cập nhật cấu trúc bảng CSDL và seed Default User."""
    app_settings = settings or get_settings()

    if app_settings.app_env != "development":
        logger.info("Bỏ qua tự động sync schema CSDL ở môi trường %s", app_settings.app_env)
        return

    logger.info("Kiểm tra kết nối CSDL và đồng bộ schema các bảng ở môi trường development...")
    engine = get_async_db_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed Default User
    async with AsyncSession(engine) as session:
        stmt = select(UserModel).where(UserModel.id == DEFAULT_USER_ID)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            logger.info("Tạo Default User trong PostgreSQL (ID: %s, Username: %s)...", DEFAULT_USER_ID, DEFAULT_USER_NAME)
            default_user = UserModel(
                id=DEFAULT_USER_ID,
                username=DEFAULT_USER_NAME,
                email=DEFAULT_USER_EMAIL,
            )
            session.add(default_user)
            await session.commit()
            logger.info("Default User đã được lưu vào database thành công!")
        else:
            logger.info("Default User đã tồn tại trong database.")

    logger.info("CSDL đã được khởi tạo và đồng bộ bảng thành công!")


if __name__ == "__main__":
    asyncio.run(init_db())
