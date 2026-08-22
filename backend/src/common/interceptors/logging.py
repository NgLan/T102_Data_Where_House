"""Interceptor ghi structured log cho application operation."""

import logging
from collections.abc import Awaitable, Callable
from typing import TypeVar

from typing_extensions import override

# isort: split
from src.common.exceptions.base import AppException
from src.common.interceptors.base import BaseInterceptor
from src.common.interceptors.context import InterceptorContext
from src.common.logging import get_logger

logger: logging.Logger = get_logger(__name__)

R = TypeVar("R")


def _event_extra(context: InterceptorContext, event: str) -> dict[str, object]:
    """Tạo structured extras chung cho operation log."""
    return {
        "event": event,
        "operation": context.operation_name,
        "request_id": context.request_id,
        "session_id": context.session_id,
    }


def _log_started(context: InterceptorContext) -> None:
    """Ghi sự kiện operation bắt đầu."""
    logger.info(
        "application_operation_started operation=%s",
        context.operation_name,
        extra=_event_extra(context, "application_operation_started"),
    )


def _log_completed(context: InterceptorContext) -> None:
    """Ghi sự kiện operation hoàn thành cùng duration nếu có."""
    extra = _event_extra(context, "application_operation_completed")
    duration = context.metadata.get("duration_ms")
    if isinstance(duration, int | float):
        extra["duration_ms"] = duration
    logger.info(
        "application_operation_completed operation=%s duration_ms=%s",
        context.operation_name,
        duration if duration is not None else "unknown",
        extra=extra,
    )


def _log_business_failure(context: InterceptorContext, exc: AppException) -> None:
    """Ghi business failure ở mức warning với error code ổn định."""
    extra = _event_extra(context, "application_operation_failed")
    extra["error_code"] = exc.code.value
    logger.warning(
        "application_operation_failed operation=%s code=%s message=%s",
        context.operation_name,
        exc.code.value,
        exc.message,
        extra=extra,
    )


def _log_system_failure(context: InterceptorContext) -> None:
    """Ghi system failure cùng traceback để điều tra."""
    logger.exception(
        "application_operation_failed operation=%s",
        context.operation_name,
        extra=_event_extra(context, "application_operation_failed"),
    )


class LoggingInterceptor(BaseInterceptor):
    """Ghi lifecycle operation và bảo toàn exception/return value."""

    @override
    async def intercept(
        self,
        context: InterceptorContext,
        call_next: Callable[[], Awaitable[R]],
    ) -> R:
        """Ghi started, completed hoặc failed quanh operation."""
        _log_started(context)
        try:
            result = await call_next()
        except AppException as exc:
            _log_business_failure(context, exc)
            raise
        except Exception:
            _log_system_failure(context)
            raise
        _log_completed(context)
        return result
