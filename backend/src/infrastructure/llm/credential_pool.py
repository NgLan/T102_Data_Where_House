"""Credential pool round-robin, cooldown và disable theo provider."""

import asyncio
from collections.abc import Callable
from datetime import datetime, timedelta

from src.common.utils.datetime import utc_now
from src.infrastructure.llm.api_credential import ApiCredential, CredentialLease, CredentialStatus
from src.infrastructure.llm.provider_types import LlmProvider


class CredentialPool:
    """Quản lý credential của đúng một provider trong một process."""

    def __init__(
        self,
        credentials: tuple[ApiCredential, ...],
        cooldown_seconds: float,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        if not credentials or len({item.provider for item in credentials}) != 1:
            raise ValueError("Credential pool phải có key của đúng một provider.")
        self._credentials = credentials
        self._cooldown_seconds = cooldown_seconds
        self._clock = clock
        self._cursor = 0
        self._lock = asyncio.Lock()

    @property
    def provider(self) -> LlmProvider:
        """Trả provider sở hữu pool."""
        return self._credentials[0].provider

    @property
    def configured_count(self) -> int:
        """Trả số credential mà không làm lộ secret."""
        return len(self._credentials)

    async def acquire(self, attempted: frozenset[str]) -> CredentialLease | None:
        """Lấy credential available kế tiếp theo round-robin."""
        async with self._lock:
            self._restore_cooled_down()
            for offset in range(self.configured_count):
                index = (self._cursor + offset) % self.configured_count
                credential = self._credentials[index]
                if self._can_acquire(credential, attempted):
                    self._cursor = (index + 1) % self.configured_count
                    return CredentialLease(credential.key_id, credential.secret)
        return None

    async def mark_succeeded(self, key_id: str) -> None:
        """Reset failure state nếu credential chưa bị coroutine khác vô hiệu hóa."""
        async with self._lock:
            credential = self._find(key_id)
            if credential.status is CredentialStatus.AVAILABLE:
                credential.consecutive_failures = 0

    async def mark_rate_limited(self, key_id: str) -> None:
        """Đưa credential vào cooldown có thời hạn."""
        async with self._lock:
            credential = self._find(key_id)
            if credential.status is not CredentialStatus.DISABLED:
                credential.status = CredentialStatus.COOLDOWN
                credential.cooldown_until = self._clock() + timedelta(seconds=self._cooldown_seconds)
                credential.consecutive_failures += 1

    async def disable(self, key_id: str) -> None:
        """Disable credential cho tới khi process được khởi động lại."""
        async with self._lock:
            credential = self._find(key_id)
            credential.status = CredentialStatus.DISABLED
            credential.cooldown_until = None
            credential.consecutive_failures += 1

    async def status(self, key_id: str) -> CredentialStatus:
        """Đọc trạng thái an toàn cho health/test."""
        async with self._lock:
            self._restore_cooled_down()
            return self._find(key_id).status

    async def has_available(self) -> bool:
        """Kiểm tra credential usable mà không thay đổi round-robin cursor."""
        async with self._lock:
            self._restore_cooled_down()
            return any(item.status is CredentialStatus.AVAILABLE for item in self._credentials)

    def _restore_cooled_down(self) -> None:
        now = self._clock()
        for credential in self._credentials:
            if credential.status is CredentialStatus.COOLDOWN and credential.cooldown_until <= now:
                credential.status = CredentialStatus.AVAILABLE
                credential.cooldown_until = None

    def _find(self, key_id: str) -> ApiCredential:
        return next(item for item in self._credentials if item.key_id == key_id)

    @staticmethod
    def _can_acquire(credential: ApiCredential, attempted: frozenset[str]) -> bool:
        return credential.key_id not in attempted and credential.status is CredentialStatus.AVAILABLE
