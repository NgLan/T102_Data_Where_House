"""Cung cấp session factory và dependency injection cho SQLAlchemy Database Sessions."""

from collections.abc import AsyncGenerator, Generator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.common.logging import get_logger
from src.infrastructure.database.config import (
    get_async_db_engine,
    get_sync_db_engine,
)

logger = get_logger(__name__)

AsyncSessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=get_async_db_engine(),
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

SyncSessionFactory: sessionmaker[Session] = sessionmaker(
    bind=get_sync_db_engine(),
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Tạo và quản lý session bất đồng bộ (AsyncSession) cho FastAPI dependency."""
    session: AsyncSession = AsyncSessionFactory()
    try:
        yield session
    except SQLAlchemyError as exc:
        logger.error("Xảy ra lỗi CSDL bất đồng bộ: %s", exc)
        await session.rollback()
        raise InfrastructureException(
            code=ErrorCode.DATABASE_ERROR,
            message="Xảy ra lỗi thao tác CSDL bất đồng bộ.",
        ) from exc
    finally:
        await session.close()


def get_sync_db_session() -> Generator[Session, None, None]:
    """Tạo và quản lý session đồng bộ (Session) cho các tác vụ đồng bộ."""
    session: Session = SyncSessionFactory()
    try:
        yield session
    except SQLAlchemyError as exc:
        logger.error("Xảy ra lỗi CSDL đồng bộ: %s", exc)
        session.rollback()
        raise InfrastructureException(
            code=ErrorCode.DATABASE_ERROR,
            message="Xảy ra lỗi thao tác CSDL đồng bộ.",
        ) from exc
    finally:
        session.close()
