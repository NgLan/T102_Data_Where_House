"""Pool API key LLM an toàn cho nhiều coroutine trong một process."""

import asyncio
from dataclasses import dataclass
from enum import StrEnum

from pydantic import SecretStr


class LlmKeyState(StrEnum):
    """Trạng thái runtime không chứa hoặc suy ngược được secret."""

    ACTIVE = "ACTIVE"
    DISABLED_FOR_PROCESS = "DISABLED_FOR_PROCESS"


@dataclass(frozen=True, slots=True)
class LlmKeyLease:
    """Key slot được cấp cho đúng một lần thử provider."""

    slot: int
    key: SecretStr


class LlmApiKeyPool:
    """Chọn key theo current-slot và lưu trạng thái dùng chung trong process."""

    def __init__(self, keys: tuple[SecretStr, ...]) -> None:
        if not keys:
            raise ValueError("LLM API key pool phải có ít nhất một slot.")
        self._keys = keys
        self._states = [LlmKeyState.ACTIVE for _ in keys]
        self._current_slot = 0
        self._lock = asyncio.Lock()

    @property
    def configured_key_count(self) -> int:
        """Trả số slot cấu hình mà không làm lộ nội dung key."""
        return len(self._keys)

    async def acquire(self, attempted_slots: frozenset[int]) -> LlmKeyLease | None:
        """Lấy slot active kế tiếp chưa được thử trong invocation hiện tại."""
        async with self._lock:
            for offset in range(self.configured_key_count):
                slot = (self._current_slot + offset) % self.configured_key_count
                if self._is_available(slot, attempted_slots):
                    return LlmKeyLease(slot, self._keys[slot])
        return None

    async def mark_succeeded(self, slot: int) -> None:
        """Giữ slot thành công làm current nếu nó chưa bị coroutine khác vô hiệu hóa."""
        async with self._lock:
            if self._states[slot] is LlmKeyState.ACTIVE:
                self._current_slot = slot

    async def mark_failed(self, slot: int, disable: bool) -> None:
        """Vô hiệu hóa khi cần và dịch current slot mà không ghi đè tiến trình mới hơn."""
        async with self._lock:
            if disable:
                self._states[slot] = LlmKeyState.DISABLED_FOR_PROCESS
            if self._current_slot == slot:
                self._current_slot = (slot + 1) % self.configured_key_count

    async def state(self, slot: int) -> LlmKeyState:
        """Đọc trạng thái slot phục vụ health nội bộ và unit test."""
        async with self._lock:
            return self._states[slot]

    def _is_available(self, slot: int, attempted_slots: frozenset[int]) -> bool:
        return slot not in attempted_slots and self._states[slot] is LlmKeyState.ACTIVE
