"""Dependency Injection cho xác thực người dùng (Authentication Dependency)."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.user.entities import User
from src.infrastructure.database.constants import (
    DEFAULT_USER_EMAIL,
    DEFAULT_USER_ID,
    DEFAULT_USER_NAME,
)
from src.infrastructure.database.session import get_async_db_session
from src.infrastructure.repositories.postgres_user_repository import (
    PostgresUserRepository,
)


async def get_current_user(
    session: AsyncSession = Depends(get_async_db_session),
) -> User:
    """Lấy thông tin người dùng hiện tại từ Database.

    Trong giai đoạn MVP: Tự động tra cứu và trả về Default User thật từ bảng users trong CSDL.
    Khi triển khai Auth chính thức: Sẽ giải mã JWT Token từ Authorization Header.
    """
    user_repo = PostgresUserRepository(session)
    user = await user_repo.get_by_id(DEFAULT_USER_ID)

    if not user:
        # Nếu chưa có, tự động tạo Default User thật trong database
        new_user = User(
            id=DEFAULT_USER_ID,
            username=DEFAULT_USER_NAME,
            email=DEFAULT_USER_EMAIL,
        )
        user = await user_repo.save(new_user)

    return user


CurrentUserDependency = Annotated[
    User,
    Depends(get_current_user),
]
