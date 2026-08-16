"""Giao diện Unit of Work quản lý ranh giới giao dịch (Transaction Boundary) cho Use Case.

Tầng Application dùng abstraction này để chốt hoặc hủy giao dịch mà không phụ thuộc vào
bất kỳ công nghệ lưu trữ cụ thể nào (SQLAlchemy, Redis...). Phần hiện thực nằm ở tầng
Infrastructure (`src/infrastructure/transaction/`).
"""

from abc import ABC, abstractmethod
from types import TracebackType


class IUnitOfWork(ABC):
    """Interface trừu tượng quản lý một đơn vị công việc có tính giao dịch.

    Dùng như một async context manager: khi thoát khỏi khối `async with` mà có ngoại lệ,
    giao dịch phải được rollback tự động.
    """

    async def __aenter__(self) -> "IUnitOfWork":
        """Mở một đơn vị công việc mới."""
        return self

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Đóng đơn vị công việc, tự động rollback nếu có ngoại lệ xảy ra."""
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Chốt toàn bộ thay đổi trong đơn vị công việc xuống nơi lưu trữ."""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Hủy toàn bộ thay đổi chưa được chốt trong đơn vị công việc."""
        pass
