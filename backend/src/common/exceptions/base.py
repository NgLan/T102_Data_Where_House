"""Lớp ngoại lệ cơ sở (Base Exception) cho toàn bộ ứng dụng."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from src.common.exceptions.error_codes import ErrorCode

ExceptionDetailValue = str | list[str]


@runtime_checkable
class ExceptionDetailPayload(Protocol):
    """Contract trung lập cho một phần tử details có thể serialize."""

    def to_dict(self) -> dict[str, ExceptionDetailValue]: ...


@dataclass(frozen=True, slots=True)
class ExceptionDetail:
    """Chi tiết lỗi trung lập với HTTP và framework."""

    field: str
    message: str

    def to_dict(self) -> dict[str, ExceptionDetailValue]:
        """Chuyển chi tiết lỗi sang dữ liệu JSON.

        Returns:
            Dictionary gồm đúng hai trường ``field`` và ``message``.
        """
        return {"field": self.field, "message": self.message}


class AppException(Exception):  # noqa: N818
    """Lớp ngoại lệ cơ bản của hệ thống.

    Không phụ thuộc vào bất kỳ HTTP framework nào (FastAPI, Starlette).
    """

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: Sequence[ExceptionDetailPayload] | None = None,
    ) -> None:
        """Khởi tạo AppException.

        Args:
            code: Mã lỗi dạng ErrorCode Enum.
            message: Thông điệp lỗi mô tả cho người dùng.
            details: Danh sách chi tiết lỗi theo field (nếu có).

        Raises:
            TypeError: Khi details chứa phần tử không phải ``ExceptionDetail``.
        """
        if details and not all(
            isinstance(detail, ExceptionDetailPayload) for detail in details
        ):
            raise TypeError("details chỉ được chứa payload có contract hợp lệ.")
        super().__init__(message)
        self.code: ErrorCode = code
        self.message: str = message
        self.details: tuple[ExceptionDetailPayload, ...] | None = (
            tuple(details) if details else None
        )

    def __repr__(self) -> str:
        """Chuỗi đại diện cho đối tượng Exception."""
        return (
            f"{self.__class__.__name__}("
            f"code={self.code!r}, message={self.message!r}, details={self.details!r})"
        )

    def __str__(self) -> str:
        """Chuỗi hiển thị mô tả lỗi."""
        return f"[{self.code}] {self.message}"
