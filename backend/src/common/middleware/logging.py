"""Pure ASGI middleware ghi log vòng đời HTTP request."""

import logging
import time

from starlette.types import ASGIApp, Message, Receive, Scope, Send

# isort: split
from src.common.logging.logger import get_logger

logger: logging.Logger = get_logger(__name__)

MILLISECONDS_PER_SECOND = 1_000
DURATION_PRECISION = 2
QUIET_PATHS = frozenset({"/health", "/healthz", "/ready", "/readyz"})


def _duration_ms(start_time: float) -> float:
    """Tính duration theo monotonic clock."""
    elapsed = (time.perf_counter() - start_time) * MILLISECONDS_PER_SECOND
    return round(elapsed, DURATION_PRECISION)


def _log_completed(scope: Scope, status_code: int, duration_ms: float) -> None:
    """Ghi sự kiện HTTP hoàn thành với structured extras."""
    method = scope.get("method", "UNKNOWN")
    path = scope.get("path", "")
    log_method = logger.debug if path in QUIET_PATHS or method == "OPTIONS" else logger.info
    log_method(
        "http_request_completed method=%s path=%s status=%d duration_ms=%.2f",
        method,
        path,
        status_code,
        duration_ms,
        extra={"event": "http_request_completed", "duration_ms": duration_ms},
    )


class HTTPLoggingMiddleware:
    """Quan sát HTTP request mà không đọc hoặc thay đổi response body."""

    def __init__(self, app: ASGIApp) -> None:
        """Khởi tạo middleware.

        Args:
            app: ASGI application phía trong.
        """
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Ghi status và duration cho một HTTP request."""
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return
        await self._observe_http(scope, receive, send)

    async def _observe_http(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Quan sát một HTTP connection và bảo toàn exception."""
        started_at = time.perf_counter()
        status_code = 500

        async def _capture_status(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
            await send(message)

        try:
            await self._app(scope, receive, _capture_status)
        except Exception:
            duration = _duration_ms(started_at)
            logger.error(
                "http_request_failed method=%s path=%s duration_ms=%.2f",
                scope.get("method", "UNKNOWN"),
                scope.get("path", ""),
                duration,
                extra={"event": "http_request_failed", "duration_ms": duration},
            )
            raise
        _log_completed(scope, status_code, _duration_ms(started_at))
