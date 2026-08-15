"""Triển khai Unit of Work bằng SQLAlchemy AsyncSession."""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.common.unit_of_work import IUnitOfWork
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from typing_extensions import override


class SqlAlchemyUnitOfWork(IUnitOfWork):
    """Quản lý transaction SQLAlchemy cho một application operation."""

    def __init__(self, session: AsyncSession) -> None:
        """Khởi tạo Unit of Work với session dùng chung repository."""
        self._session = session

    @override
    async def commit(self) -> None:
        """Commit transaction và chuyển đổi lỗi hạ tầng theo chuẩn."""
        try:
            await self._session.commit()
        except SQLAlchemyError as exc:
            await self._session.rollback()
            raise InfrastructureException(
                code=ErrorCode.DATABASE_ERROR,
                message="Không thể commit.",
            ) from exc

    @override
    async def rollback(self) -> None:
        """Rollback transaction hiện tại."""
        await self._session.rollback()
