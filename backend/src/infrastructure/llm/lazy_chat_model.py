"""Protocol và lazy provider dùng chung cho các Agent adapter."""

from collections.abc import Callable
from typing import Protocol

from pydantic import BaseModel


class StructuredModel(Protocol):
    """Contract runnable structured output tối thiểu."""

    async def ainvoke(self, messages: list[object]) -> BaseModel:
        """Gọi model với danh sách message."""
        ...


class StructuredChatModel(Protocol):
    """Contract chat model duy nhất mà Agent infrastructure cần."""

    def with_structured_output(self, schema: type[BaseModel]) -> StructuredModel:
        """Bind schema output mà không làm lộ provider cụ thể."""
        ...


ChatModelSource = StructuredChatModel | Callable[[], StructuredChatModel]


class LazyChatModel:
    """Chỉ khởi tạo chat model khi use case AI thực sự chạy."""

    def __init__(self, source: ChatModelSource) -> None:
        """Lưu model hoặc factory mà chưa gọi factory."""
        self._source = source
        self._model: StructuredChatModel | None = None

    def get(self) -> StructuredChatModel:
        """Trả model đã cache hoặc tạo model ở lần gọi đầu."""
        if self._model is None:
            self._model = self._source() if callable(self._source) else self._source
        return self._model
