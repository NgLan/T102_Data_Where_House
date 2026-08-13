"""Unit tests cho TimingInterceptor (test_timing.py)."""

import asyncio

import pytest
from src.common.interceptors.context import InterceptorContext
from src.common.interceptors.timing import TimingInterceptor


@pytest.mark.asyncio
async def test_timing_interceptor_duration_calculation() -> None:
    """Kiểm tra TimingInterceptor tính toán duration_ms chính xác khi operation chạy."""
    interceptor = TimingInterceptor()
    context = InterceptorContext.create("SlowOperation")

    async def slow_op() -> str:
        await asyncio.sleep(0.05)  # 50ms
        return "DONE"

    result = await interceptor.intercept(context, slow_op)

    assert result == "DONE"
    assert "duration_ms" in context.metadata
    duration_ms = context.metadata["duration_ms"]
    assert isinstance(duration_ms, float)
    assert duration_ms >= 40.0  # Cho phép khoảng dung sai khi sleep


@pytest.mark.asyncio
async def test_timing_interceptor_records_duration_on_exception() -> None:
    """Kiểm tra TimingInterceptor vẫn ghi nhận duration_ms khi operation bị lỗi."""
    interceptor = TimingInterceptor()
    context = InterceptorContext.create("FailingTimedOperation")

    async def failing_op() -> None:
        await asyncio.sleep(0.02)
        raise ValueError("Timed out or failed")

    with pytest.raises(ValueError, match="Timed out or failed"):
        await interceptor.intercept(context, failing_op)

    assert "duration_ms" in context.metadata
    assert context.metadata["duration_ms"] >= 10.0
