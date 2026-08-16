"""Hiện thực Unit of Work trên SQLAlchemy AsyncSession."""

from types import TracebackType

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.common.unit_of_work import IUnitOfWork
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.common.logging import get_logger

logger = get_logger(__name__)


class SqlAlchemyUnitOfWork(IUnitOfWork):
    """Quản lý giao dịch trên cùng một AsyncSession mà các Repository đang sử dụng.

    Session được cấp phát ở tầng Presentation theo vòng đời của một HTTP request, nên
    Unit of Work và mọi Repository trong cùng request đều thao tác trên một giao dịch duy nhất.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Khởi tạo đơn vị công việc với AsyncSession của request hiện tại."""
        self._session: AsyncSession = session

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Rollback giao dịch nếu khối `async with` kết thúc do có ngoại lệ."""
        if exc_type is not None:
            await self.rollback()

    async def commit(self) -> None:
        """Chốt giao dịch hiện tại xuống CSDL."""
        try:
            await self._session.commit()
        except SQLAlchemyError as exc:
            await self.rollback()
            logger.exception("Chốt giao dịch CSDL thất bại, đã rollback.")
            raise InfrastructureException(
                code=ErrorCode.DATABASE_ERROR,
                message="Không thể chốt giao dịch xuống cơ sở dữ liệu.",
            ) from exc

    async def rollback(self) -> None:
        """Hủy toàn bộ thay đổi chưa được chốt của giao dịch hiện tại."""
        try:
            await self._session.rollback()
        except SQLAlchemyError as exc:
            logger.exception("Rollback giao dịch CSDL thất bại.")
            raise InfrastructureException(
                code=ErrorCode.DATABASE_ERROR,
                message="Không thể hủy giao dịch cơ sở dữ liệu.",
            ) from exc
