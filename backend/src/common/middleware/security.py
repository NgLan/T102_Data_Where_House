"""Pure ASGI middleware thiết lập các security header dùng chung."""

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

HSTS_MAX_AGE_SECONDS = 31_536_000
BASE_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}


class SecurityHeadersMiddleware:
    """Đính kèm security header mà không buffer response body."""

    def __init__(self, app: ASGIApp, enable_hsts: bool = False) -> None:
        """Khởi tạo middleware.

        Args:
            app: ASGI application phía trong.
            enable_hsts: Có phát HSTS cho môi trường HTTPS hay không.
        """
        self._app = app
        self._enable_hsts = enable_hsts

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Đính kèm header khi ASGI bắt đầu gửi HTTP response."""
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        async def _send_with_security_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                for name, value in BASE_SECURITY_HEADERS.items():
                    headers[name] = value
                if self._enable_hsts:
                    headers["Strict-Transport-Security"] = (
                        f"max-age={HSTS_MAX_AGE_SECONDS}; includeSubDomains"
                    )
            await send(message)

        await self._app(scope, receive, _send_with_security_headers)
