"""PostgreSQL repository cho thực thể User."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.shared.types import EntityID
from src.domain.user.entities import User
from src.domain.user.i_user_repository import IUserRepository
from src.infrastructure.database.error_translation import translate_database_errors
from src.infrastructure.database.mappers.user_mapper import UserMapper
from src.infrastructure.database.models.user import UserModel
from src.infrastructure.repositories.sqlalchemy_crud import SqlAlchemyCrud
from typing_extensions import override


class PostgresUserRepository(IUserRepository):
    """Lưu trữ User bằng SQLAlchemy AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._crud = SqlAlchemyCrud(session, UserModel, UserMapper)

    @override
    async def get_by_id(self, entity_id: EntityID) -> User | None:
        """Lấy người dùng theo ID."""
        return await self._crud.get_by_id(entity_id)

    @override
    @translate_database_errors
    async def get_by_username(self, username: str) -> User | None:
        """Lấy người dùng theo tên đăng nhập."""
        result = await self._session.execute(select(UserModel).where(UserModel.username == username))
        model = result.scalar_one_or_none()
        return UserMapper.to_domain(model) if model else None

    @override
    @translate_database_errors
    async def get_by_email(self, email: str) -> User | None:
        """Lấy người dùng theo email."""
        result = await self._session.execute(select(UserModel).where(UserModel.email == email))
        model = result.scalar_one_or_none()
        return UserMapper.to_domain(model) if model else None

    @override
    async def save(self, entity: User) -> User:
        """Lưu mới hoặc cập nhật người dùng."""
        return await self._crud.save(entity)

    @override
    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa người dùng theo ID."""
        return await self._crud.delete(entity_id)
