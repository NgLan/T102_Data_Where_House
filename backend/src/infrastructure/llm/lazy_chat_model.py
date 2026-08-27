"""Protocol và lazy provider dùng chung cho các Agent adapter."""

from collections.abc import Callable
from typing import Protocol

from pydantic import BaseModel


class StructuredModel(Protocol):
    """Contract runnable structured output tối thiểu."""

    async def ainvoke(self, messages: list[object]) -> BaseModel | dict[str, object]:
        """Gọi model với danh sách message."""
        ...


class ILLMGateway(Protocol):
    """Contract gateway provider-neutral mà Agent infrastructure phụ thuộc."""

    def with_structured_output(
        self,
        schema: type[BaseModel],
        *,
        include_raw: bool = False,
    ) -> StructuredModel:
        """Bind schema output mà không làm lộ provider cụ thể."""
        ...


LlmGatewaySource = ILLMGateway | Callable[[], ILLMGateway]


class LazyLlmGateway:
    """Chỉ khởi tạo gateway khi use case AI thực sự chạy."""

    def __init__(self, source: LlmGatewaySource) -> None:
        """Lưu gateway hoặc factory mà chưa gọi factory."""
        self._source = source
        self._gateway: ILLMGateway | None = None

    def get(self) -> ILLMGateway:
        """Trả gateway đã cache hoặc tạo gateway ở lần gọi đầu."""
        if self._gateway is None:
            self._gateway = self._source() if callable(self._source) else self._source
        return self._gateway
