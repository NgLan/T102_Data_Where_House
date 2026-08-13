"""Unit tests kiểm tra tính độc lập và cách ly bất đồng bộ của Interceptors (test_isolation.py)."""

import asyncio
import sys

import pytest
from src.common.interceptors import (
    InterceptorChain,
    LoggingInterceptor,
    TimingInterceptor,
)
from src.common.interceptors.context import InterceptorContext
from src.common.logging.context import clear_logging_context, set_request_id


def test_no_fastapi_dependency_in_interceptors() -> None:
    """Chứng minh generic Interceptors không import FastAPI hay HTTP modules."""
    forbidden_modules = ["fastapi", "starlette"]

    # Lấy các module đã được import bởi package interceptors
    import src.common.interceptors as interceptors_pkg

    assert interceptors_pkg.__name__ == "src.common.interceptors"

    for loaded_mod in list(sys.modules.keys()):
        if loaded_mod.startswith("src.common.interceptors"):
            for forbidden in forbidden_modules:
                assert forbidden not in sys.modules[loaded_mod].__dict__, (
                    f"Phát hiện import cấm '{forbidden}' trong {loaded_mod}"
                )


@pytest.mark.asyncio
async def test_async_context_isolation_under_concurrency() -> None:
    """Kiểm tra tính cách ly ngữ cảnh (request_id, session_id) khi chạy đồng thời (asyncio.gather)."""
    chain = InterceptorChain([TimingInterceptor(), LoggingInterceptor()])

    async def run_operation(op_name: str, req_id: str, delay: float) -> dict[str, str | None]:
        set_request_id(req_id)
        ctx = InterceptorContext.create(op_name)
        await asyncio.sleep(delay)

        async def dummy_task() -> str:
            return f"Done {op_name}"

        await chain.execute(ctx, dummy_task)
        result_req_id = ctx.request_id
        clear_logging_context()
        return {"op": op_name, "req_id": result_req_id}

    # Chạy 3 operations bất đồng bộ đồng thời với thời gian sleep khác nhau
    task1 = run_operation("Op1", "req_AAA", 0.03)
    task2 = run_operation("Op2", "req_BBB", 0.01)
    task3 = run_operation("Op3", "req_CCC", 0.02)

    results = await asyncio.gather(task1, task2, task3)

    assert results[0] == {"op": "Op1", "req_id": "req_AAA"}
    assert results[1] == {"op": "Op2", "req_id": "req_BBB"}
    assert results[2] == {"op": "Op3", "req_id": "req_CCC"}
