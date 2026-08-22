"""Interceptor gắn audit metadata đã được whitelist."""

from collections.abc import Awaitable, Callable
from typing import TypeVar

from typing_extensions import override

# isort: split
from src.common.interceptors.base import BaseInterceptor
from src.common.interceptors.context import InterceptorContext
from src.common.utils.datetime import to_isoformat, utc_now

R = TypeVar("R")
DEFAULT_AUDIT_ACTOR = "system"


class AuditInterceptor(BaseInterceptor):
    """Chỉ gắn actor, action, resource ID và timestamp vào context."""

    def __init__(
        self,
        actor: str | None = None,
        action: str | None = None,
        resource_id: str | None = None,
    ) -> None:
        """Khởi tạo audit descriptor không chứa dữ liệu nhạy cảm."""
        self._actor = actor
        self._action = action
        self._resource_id = resource_id

    @override
    async def intercept(
        self,
        context: InterceptorContext,
        call_next: Callable[[], Awaitable[R]],
    ) -> R:
        """Gắn audit record đã whitelist rồi tiếp tục operation."""
        audit_record: dict[str, object] = {
            "timestamp": to_isoformat(utc_now()),
            "actor": self._actor or context.metadata.get("actor", DEFAULT_AUDIT_ACTOR),
            "action": self._action or context.operation_name,
        }
        resource_id = self._resource_id or context.metadata.get("resource_id")
        if resource_id is not None:
            audit_record["resource_id"] = resource_id
        context.metadata["audit"] = audit_record
        return await call_next()
