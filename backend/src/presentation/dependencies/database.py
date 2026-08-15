"""Dependency Injection cấp phát phiên làm việc CSDL cho tầng Presentation."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.session import get_async_db_session


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Cấp phát AsyncSession cho một request HTTP."""
    async for session in get_async_db_session():
        yield session


DbSession = Annotated[AsyncSession, Depends(get_db_session)]
