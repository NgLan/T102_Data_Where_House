"""Abstraction và composition chain cho application interceptor."""

import functools
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar

from src.common.interceptors.context import InterceptorContext

P = ParamSpec("P")
R = TypeVar("R")


class BaseInterceptor(ABC):
    """Hợp đồng interceptor bảo toàn exception và return value."""

    @abstractmethod
    async def intercept(
        self,
        context: InterceptorContext,
        call_next: Callable[[], Awaitable[R]],
    ) -> R:
        """Thực thi logic quan sát quanh operation.

        Args:
            context: Ngữ cảnh operation hiện tại.
            call_next: Operation kế tiếp trong chain.

        Returns:
            Chính xác giá trị do operation trả về.
        """
        ...


class InterceptorChain:
    """Phối hợp interceptor theo thứ tự bọc từ trái sang phải."""

    def __init__(self, interceptors: list[BaseInterceptor] | None = None) -> None:
        """Khởi tạo chain từ danh sách interceptor."""
        self._interceptors = list(interceptors or [])

    def add_interceptor(self, interceptor: BaseInterceptor) -> "InterceptorChain":
        """Thêm interceptor vào cuối chain và trả lại chain."""
        self._interceptors.append(interceptor)
        return self

    async def execute(
        self,
        context: InterceptorContext,
        target: Callable[[], Awaitable[R]],
    ) -> R:
        """Thực thi target qua toàn bộ interceptor theo thứ tự."""

        async def _dispatch(index: int) -> R:
            if index >= len(self._interceptors):
                return await target()
            interceptor = self._interceptors[index]
            return await interceptor.intercept(context, lambda: _dispatch(index + 1))

        return await _dispatch(0)


def intercepted(
    *interceptors: BaseInterceptor,
    operation_name: str | None = None,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """Tạo decorator áp dụng interceptor chain cho async operation."""
    chain = InterceptorChain(list(interceptors))

    def _decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @functools.wraps(func)
        async def _wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            name = operation_name or func.__name__
            context = InterceptorContext.from_logging_context(name)
            return await chain.execute(context, lambda: func(*args, **kwargs))

        return _wrapper

    return _decorator
