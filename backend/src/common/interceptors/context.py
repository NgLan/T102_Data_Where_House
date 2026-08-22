"""Ngữ cảnh headless cho application interceptor."""

from collections.abc import Mapping
from dataclasses import dataclass, field

from src.common.logging.context import (
    get_correlation_id,
    get_request_id,
    get_session_id,
)


@dataclass(slots=True)
class InterceptorContext:
    """Thông tin quan sát được truyền qua một interceptor chain."""

    operation_name: str
    request_id: str | None = None
    correlation_id: str | None = None
    session_id: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)

    @classmethod
    def from_logging_context(
        cls,
        operation_name: str,
        metadata: Mapping[str, object] | None = None,
    ) -> "InterceptorContext":
        """Tạo operation context từ ContextVar hiện tại.

        Args:
            operation_name: Tên ổn định của application operation.
            metadata: Metadata không nhạy cảm ban đầu.

        Returns:
            Interceptor context độc lập với HTTP.
        """
        return cls(
            operation_name=operation_name,
            request_id=get_request_id(),
            correlation_id=get_correlation_id(),
            session_id=get_session_id(),
            metadata=dict(metadata or {}),
        )
