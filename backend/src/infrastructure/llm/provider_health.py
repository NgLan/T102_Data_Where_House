"""Provider health/cooldown đơn giản, async-safe theo process."""

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum

from src.common.utils.datetime import utc_now
from src.infrastructure.llm.provider_types import LlmProvider


class ProviderStatus(StrEnum):
    """Trạng thái provider dùng cho routing."""

    AVAILABLE = "AVAILABLE"
    COOLDOWN = "COOLDOWN"


@dataclass(slots=True)
class ProviderHealth:
    """Health state không chứa credential hoặc raw provider error."""

    status: ProviderStatus = ProviderStatus.AVAILABLE
    consecutive_failures: int = 0
    cooldown_until: datetime | None = None


class ProviderHealthRegistry:
    """Theo dõi health cho toàn bộ registered provider."""

    def __init__(
        self,
        providers: tuple[LlmProvider, ...],
        policy: tuple[int, float],
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._states = {provider: ProviderHealth() for provider in providers}
        self._failure_threshold, self._cooldown_seconds = policy
        self._clock = clock
        self._lock = asyncio.Lock()

    async def is_available(self, provider: LlmProvider) -> bool:
        """Trả availability và tự khôi phục provider hết cooldown."""
        async with self._lock:
            state = self._states[provider]
            self._restore(state)
            return state.status is ProviderStatus.AVAILABLE

    async def mark_succeeded(self, provider: LlmProvider) -> None:
        """Reset provider health sau network call thành công."""
        async with self._lock:
            state = self._states[provider]
            state.status = ProviderStatus.AVAILABLE
            state.consecutive_failures = 0
            state.cooldown_until = None

    async def mark_failed(self, provider: LlmProvider) -> bool:
        """Tăng failure count và trả True khi provider vừa vào cooldown."""
        async with self._lock:
            state = self._states[provider]
            state.consecutive_failures += 1
            if state.consecutive_failures < self._failure_threshold:
                return False
            state.status = ProviderStatus.COOLDOWN
            state.cooldown_until = self._clock() + timedelta(seconds=self._cooldown_seconds)
            return True

    async def status(self, provider: LlmProvider) -> ProviderStatus:
        """Đọc trạng thái phục vụ health/test."""
        async with self._lock:
            state = self._states[provider]
            self._restore(state)
            return state.status

    def _restore(self, state: ProviderHealth) -> None:
        if state.status is ProviderStatus.COOLDOWN and state.cooldown_until <= self._clock():
            state.status = ProviderStatus.AVAILABLE
            state.consecutive_failures = 0
            state.cooldown_until = None

