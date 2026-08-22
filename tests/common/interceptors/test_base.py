"""Unit tests cho BaseInterceptor, InterceptorChain và @intercepted decorator (test_base.py)."""

from collections.abc import Awaitable, Callable
from typing import Any

import pytest
from src.common.interceptors.base import (
    BaseInterceptor,
    InterceptorChain,
    intercepted,
)
from src.common.interceptors.context import InterceptorContext


class TrackingInterceptor(BaseInterceptor):
    """Interceptor trợ giúp ghi nhận thứ tự thực thi để kiểm thử."""

    def __init__(self, name: str, execution_log: list[str]) -> None:
        self.name = name
        self.execution_log = execution_log

    async def intercept(
        self,
        context: InterceptorContext,
        call_next: Callable[[], Awaitable[Any]],
    ) -> Any:
        self.execution_log.append(f"{self.name}:before")
        try:
            res = await call_next()
            self.execution_log.append(f"{self.name}:after")
            return res
        except Exception as e:
            self.execution_log.append(f"{self.name}:error")
            raise e


@pytest.mark.asyncio
async def test_interceptor_chain_order() -> None:
    """Kiểm tra thứ tự thực thi chuỗi InterceptorChain lồng nhau."""
    logs: list[str] = []
    i1 = TrackingInterceptor("I1", logs)
    i2 = TrackingInterceptor("I2", logs)

    chain = InterceptorChain([i1, i2])
    context = InterceptorContext("TestOperation")

    async def target_op() -> str:
        logs.append("TargetExecuted")
        return "SUCCESS"

    result = await chain.execute(context, target_op)

    assert result == "SUCCESS"
    assert logs == [
        "I1:before",
        "I2:before",
        "TargetExecuted",
        "I2:after",
        "I1:after",
    ]


@pytest.mark.asyncio
async def test_interceptor_chain_exception_propagation() -> None:
    """Kiểm tra ngoại lệ được propagate và các interceptor bắt được error event."""
    logs: list[str] = []
    i1 = TrackingInterceptor("I1", logs)
    i2 = TrackingInterceptor("I2", logs)

    chain = InterceptorChain([i1, i2])
    context = InterceptorContext("FailingOperation")

    async def failing_op() -> None:
        logs.append("TargetFailing")
        raise RuntimeError("Operation Failed")

    with pytest.raises(RuntimeError, match="Operation Failed"):
        await chain.execute(context, failing_op)

    assert logs == [
        "I1:before",
        "I2:before",
        "TargetFailing",
        "I2:error",
        "I1:error",
    ]


@pytest.mark.asyncio
async def test_intercepted_decorator() -> None:
    """Kiểm tra decorator @intercepted bọc hàm async chính xác."""
    logs: list[str] = []
    i1 = TrackingInterceptor("I1", logs)

    @intercepted(i1, operation_name="CustomDecoratorOp")
    async def sample_use_case(val: int) -> int:
        logs.append(f"UseCase:{val}")
        return val * 2

    res = await sample_use_case(5)

    assert res == 10
    assert logs == ["I1:before", "UseCase:5", "I1:after"]
