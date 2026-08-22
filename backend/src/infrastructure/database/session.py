"""Cấp phát SQLAlchemy AsyncSession theo vòng đời request."""

from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from src.infrastructure.database.config import get_async_db_engine


@lru_cache
def get_async_session_factory() -> async_sessionmaker[AsyncSession]:
    """Tạo lazy async session factory dùng chung."""
    return async_sessionmaker(
        bind=get_async_db_engine(),
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )


async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield session; Application Unit of Work sở hữu transaction."""
    async with get_async_session_factory()() as session:
        yield session
