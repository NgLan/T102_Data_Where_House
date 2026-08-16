"""Chuyển đổi lỗi SQLAlchemy tại infrastructure boundary."""

from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any, TypeVar, cast

from sqlalchemy.exc import SQLAlchemyError
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException

AsyncOperation = TypeVar(
    "AsyncOperation",
    bound=Callable[..., Coroutine[Any, Any, Any]],
)


def translate_database_errors(
    operation: AsyncOperation,
) -> AsyncOperation:
    """Bọc async database operation và giữ nguyên chữ ký coroutine.

    Args:
        operation: Coroutine thao tác với SQLAlchemy cần dịch lỗi.

    Returns:
        Coroutine cùng parameter/return contract với operation ban đầu.

    Raises:
        InfrastructureException: Khi SQLAlchemy phát sinh lỗi cơ sở dữ liệu.
    """

    @wraps(operation)
    async def translated(
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        try:
            return await operation(*args, **kwargs)
        except SQLAlchemyError as exc:
            raise InfrastructureException(
                code=ErrorCode.DATABASE_ERROR,
                message="Không thể hoàn tất thao tác cơ sở dữ liệu.",
            ) from exc

    return cast(AsyncOperation, translated)
