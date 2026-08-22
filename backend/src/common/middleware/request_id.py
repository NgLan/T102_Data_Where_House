"""Pure ASGI middleware quản lý request và correlation ID."""

import re

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

# isort: split
from src.common.logging.context import LoggingContextSnapshot, bind_logging_context
from src.common.utils.uuid import generate_uuid_str

REQUEST_ID_HEADER = "X-Request-ID"
CORRELATION_ID_HEADER = "X-Correlation-ID"
MAX_CONTEXT_ID_LENGTH = 64
VALID_ID_PATTERN = re.compile(rf"^[a-zA-Z0-9_-]{{1,{MAX_CONTEXT_ID_LENGTH}}}$")


def _validated_id(value: str | None) -> str | None:
    """Chuẩn hóa ID an toàn cho header và log context."""
    if value is None:
        return None
    normalized = value.strip()
    return normalized if VALID_ID_PATTERN.fullmatch(normalized) else None


class RequestIDMiddleware:
    """Bind request identifiers và khôi phục ContextVar sau mỗi HTTP request."""

    def __init__(self, app: ASGIApp) -> None:
        """Khởi tạo middleware.

        Args:
            app: ASGI application phía trong.
        """
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Xử lý một ASGI connection và bỏ qua protocol ngoài HTTP."""
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return
        headers = Headers(scope=scope)
        request_id = _validated_id(headers.get(REQUEST_ID_HEADER)) or generate_uuid_str()
        correlation_id = _validated_id(headers.get(CORRELATION_ID_HEADER))
        snapshot = LoggingContextSnapshot(
            request_id=request_id,
            correlation_id=correlation_id,
        )

        async def _send_with_identifiers(message: Message) -> None:
            if message["type"] == "http.response.start":
                response_headers = MutableHeaders(scope=message)
                response_headers[REQUEST_ID_HEADER] = request_id
                if correlation_id:
                    response_headers[CORRELATION_ID_HEADER] = correlation_id
            await send(message)

        with bind_logging_context(snapshot):
            await self._app(scope, receive, _send_with_identifiers)
