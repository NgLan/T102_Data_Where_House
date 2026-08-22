"""Quản lý ngữ cảnh request và agent tracing qua ContextVars (Async / Thread-safe)."""

from contextlib import AbstractContextManager
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from types import TracebackType

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)
correlation_id_ctx: ContextVar[str | None] = ContextVar("correlation_id", default=None)
session_id_ctx: ContextVar[str | None] = ContextVar("session_id", default=None)
agent_name_ctx: ContextVar[str | None] = ContextVar("agent_name", default=None)


@dataclass(frozen=True, slots=True)
class LoggingContextSnapshot:
    """Giá trị logging context cần bind cho một luồng thực thi."""

    request_id: str | None = None
    correlation_id: str | None = None
    session_id: str | None = None
    agent_name: str | None = None


@dataclass(slots=True)
class _LoggingContextBinding(AbstractContextManager[None]):
    """Context manager một lần sử dụng cho logging context."""

    snapshot: LoggingContextSnapshot
    _tokens: tuple[Token[str | None], ...] | None = field(init=False, default=None)

    def __enter__(self) -> None:
        """Bind snapshot vào execution context hiện tại."""
        if self._tokens is not None:
            raise RuntimeError("Logging context binding không thể được tái sử dụng.")
        self._tokens = (
            request_id_ctx.set(self.snapshot.request_id),
            correlation_id_ctx.set(self.snapshot.correlation_id),
            session_id_ctx.set(self.snapshot.session_id),
            agent_name_ctx.set(self.snapshot.agent_name),
        )

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Khôi phục context trước đó kể cả khi operation phát sinh lỗi."""
        if self._tokens is None:
            raise RuntimeError("Logging context binding chưa được kích hoạt.")
        contexts = (request_id_ctx, correlation_id_ctx, session_id_ctx, agent_name_ctx)
        for context, token in zip(reversed(contexts), reversed(self._tokens), strict=True):
            context.reset(token)


def bind_logging_context(snapshot: LoggingContextSnapshot) -> AbstractContextManager[None]:
    """Tạo context binding tạm thời và có khả năng khôi phục trạng thái.

    Args:
        snapshot: Bộ giá trị cần dùng trong phạm vi context manager.

    Returns:
        Context manager dùng với câu lệnh ``with``.
    """
    return _LoggingContextBinding(snapshot)


def get_request_id() -> str | None:
    """Lấy request ID của request hiện tại."""
    return request_id_ctx.get()


def set_request_id(request_id: str | None) -> None:
    """Ghi nhận request ID cho ngữ cảnh hiện tại."""
    request_id_ctx.set(request_id)


def get_correlation_id() -> str | None:
    """Lấy correlation ID (nếu có) cho luồng truy vết đa hệ thống."""
    return correlation_id_ctx.get()


def set_correlation_id(correlation_id: str | None) -> None:
    """Ghi nhận correlation ID cho ngữ cảnh hiện tại."""
    correlation_id_ctx.set(correlation_id)


def get_session_id() -> str | None:
    """Lấy session ID của người dùng/hội thoại hiện tại."""
    return session_id_ctx.get()


def set_session_id(session_id: str | None) -> None:
    """Ghi nhận session ID cho ngữ cảnh hiện tại."""
    session_id_ctx.set(session_id)


def get_agent_name() -> str | None:
    """Lấy tên Agent operation đang thực thi trong request hiện tại."""
    return agent_name_ctx.get()


def set_agent_name(agent_name: str | None) -> None:
    """Ghi nhận tên Agent cho ngữ cảnh hiện tại."""
    agent_name_ctx.set(agent_name)


def clear_logging_context() -> None:
    """Xóa toàn bộ ngữ cảnh logging sau khi hoàn thành request hoặc task."""
    request_id_ctx.set(None)
    correlation_id_ctx.set(None)
    session_id_ctx.set(None)
    agent_name_ctx.set(None)
