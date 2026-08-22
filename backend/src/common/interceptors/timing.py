"""Interceptor đo thời gian application operation bằng monotonic clock."""

import time
from collections.abc import Awaitable, Callable
from typing import TypeVar

from typing_extensions import override

# isort: split
from src.common.interceptors.base import BaseInterceptor
from src.common.interceptors.context import InterceptorContext

R = TypeVar("R")
MILLISECONDS_PER_SECOND = 1_000
DURATION_PRECISION = 2


class TimingInterceptor(BaseInterceptor):
    """Ghi duration vào metadata mà không thay đổi operation result."""

    @override
    async def intercept(
        self,
        context: InterceptorContext,
        call_next: Callable[[], Awaitable[R]],
    ) -> R:
        """Đo operation kể cả khi operation phát sinh exception."""
        started_at = time.perf_counter()
        try:
            return await call_next()
        finally:
            elapsed = (time.perf_counter() - started_at) * MILLISECONDS_PER_SECOND
            context.metadata["duration_ms"] = round(elapsed, DURATION_PRECISION)
