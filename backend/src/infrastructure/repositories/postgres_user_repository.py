"""Triển khai PostgreSQL Repository cho thực thể User."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.shared.types import EntityID
from src.domain.user.entities import User
from src.domain.user.repository import IUserRepository
from src.infrastructure.database.mappers.user_mapper import UserMapper
from src.infrastructure.database.models.user import UserModel
from typing_extensions import override


class PostgresUserRepository(IUserRepository):
    """Triển khai IUserRepository sử dụng SQLAlchemy AsyncSession và UserMapper."""

    def __init__(self, session: AsyncSession) -> None:
        """Khởi tạo repository với SQLAlchemy AsyncSession."""
        self._session: AsyncSession = session

    @override
    async def get_by_id(self, entity_id: EntityID) -> User | None:
        """Lấy người dùng theo ID."""
        stmt = select(UserModel).where(UserModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return UserMapper.to_domain(model) if model else None

    @override
    async def get_by_username(self, username: str) -> User | None:
        """Lấy thông tin người dùng theo tên đăng nhập."""
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return UserMapper.to_domain(model) if model else None

    @override
    async def get_by_email(self, email: str) -> User | None:
        """Lấy thông tin người dùng theo địa chỉ email."""
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return UserMapper.to_domain(model) if model else None

    @override
    async def save(self, entity: User) -> User:
        """Lưu (tạo mới hoặc cập nhật) thực thể User."""
        stmt = select(UserModel).where(UserModel.id == entity.id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        if existing_model:
            model = UserMapper.update_model(existing_model, entity)
        else:
            model = UserMapper.to_model(entity)
            self._session.add(model)

        await self._session.flush()
        return UserMapper.to_domain(model)

    @override
    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa thực thể User theo ID."""
        stmt = select(UserModel).where(UserModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True
