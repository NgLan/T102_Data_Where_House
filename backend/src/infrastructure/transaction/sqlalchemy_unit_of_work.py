"""Hiện thực Unit of Work trên SQLAlchemy AsyncSession."""

from types import TracebackType
from typing import Self

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.common.unit_of_work import IUnitOfWork
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.common.logging import get_logger
from typing_extensions import override

logger = get_logger(__name__)


class SqlAlchemyUnitOfWork(IUnitOfWork):
    """Quản lý giao dịch trên cùng một AsyncSession mà các Repository đang sử dụng.

    Session được cấp phát ở tầng Presentation theo vòng đời của một HTTP request, nên
    Unit of Work và mọi Repository trong cùng request đều thao tác trên một giao dịch duy nhất.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Khởi tạo đơn vị công việc với AsyncSession của request hiện tại."""
        self._session: AsyncSession = session
        self._is_committed = False

    @override
    async def __aenter__(self) -> Self:
        """Bắt đầu một transaction boundary mới."""
        self._is_committed = False
        return self

    @override
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Rollback giao dịch nếu khối `async with` kết thúc do có ngoại lệ."""
        if exc_type is not None or not self._is_committed:
            await self.rollback()

    @override
    async def commit(self) -> None:
        """Chốt giao dịch hiện tại xuống CSDL."""
        try:
            await self._session.commit()
            self._is_committed = True
        except SQLAlchemyError as exc:
            await self.rollback()
            logger.exception("Chốt giao dịch CSDL thất bại, đã rollback.")
            raise InfrastructureException(
                code=ErrorCode.DATABASE_ERROR,
                message="Không thể chốt giao dịch xuống cơ sở dữ liệu.",
            ) from exc

    @override
    async def rollback(self) -> None:
        """Hủy toàn bộ thay đổi chưa được chốt của giao dịch hiện tại."""
        try:
            await self._session.rollback()
            self._is_committed = False
        except SQLAlchemyError as exc:
            logger.exception("Rollback giao dịch CSDL thất bại.")
            raise InfrastructureException(
                code=ErrorCode.DATABASE_ERROR,
                message="Không thể hủy giao dịch cơ sở dữ liệu.",
            ) from exc
