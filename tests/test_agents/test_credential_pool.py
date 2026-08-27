"""Unit tests cho provider-scoped credential pool."""

import asyncio
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import SecretStr
from src.infrastructure.llm.api_credential import ApiCredential, CredentialStatus
from src.infrastructure.llm.credential_pool import CredentialPool
from src.infrastructure.llm.provider_types import LlmProvider


def _pool(clock: list[datetime]) -> CredentialPool:
    credentials = tuple(
        ApiCredential(f"openai_{index:02d}", LlmProvider.OPENAI, SecretStr(f"secret-{index}"))
        for index in range(1, 4)
    )
    return CredentialPool(credentials, 60.0, lambda: clock[0])


@pytest.mark.asyncio
async def test_pool_uses_round_robin_across_successful_invocations() -> None:
    pool = _pool([datetime(2026, 1, 1, tzinfo=UTC)])

    leases = [await pool.acquire(frozenset()) for _ in range(4)]

    assert [lease.key_id for lease in leases if lease] == [
        "openai_01", "openai_02", "openai_03", "openai_01"
    ]


@pytest.mark.asyncio
async def test_rate_limited_credential_recovers_after_cooldown() -> None:
    clock = [datetime(2026, 1, 1, tzinfo=UTC)]
    pool = _pool(clock)
    lease = await pool.acquire(frozenset())
    assert lease is not None
    await pool.mark_rate_limited(lease.key_id)

    assert await pool.status(lease.key_id) is CredentialStatus.COOLDOWN
    clock[0] += timedelta(seconds=61)
    assert await pool.status(lease.key_id) is CredentialStatus.AVAILABLE


@pytest.mark.asyncio
async def test_disabled_credential_is_not_reactivated_by_late_success() -> None:
    pool = _pool([datetime(2026, 1, 1, tzinfo=UTC)])
    lease = await pool.acquire(frozenset())
    assert lease is not None

    await pool.disable(lease.key_id)
    await pool.mark_succeeded(lease.key_id)

    assert await pool.status(lease.key_id) is CredentialStatus.DISABLED


@pytest.mark.asyncio
async def test_concurrent_acquire_preserves_round_robin_cursor() -> None:
    pool = _pool([datetime(2026, 1, 1, tzinfo=UTC)])

    leases = await asyncio.gather(*(pool.acquire(frozenset()) for _ in range(6)))

    assert [lease.key_id for lease in leases if lease] == [
        "openai_01", "openai_02", "openai_03", "openai_01", "openai_02", "openai_03"
    ]
