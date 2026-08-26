"""Unit test trạng thái và concurrency primitive của LLM key pool."""

import asyncio

import pytest
from pydantic import SecretStr
from src.infrastructure.llm.api_key_pool import LlmApiKeyPool, LlmKeyState


def _pool(count: int) -> LlmApiKeyPool:
    return LlmApiKeyPool(tuple(SecretStr(f"secret-{index}") for index in range(count)))


@pytest.mark.asyncio
async def test_pool_keeps_successful_slot_as_current() -> None:
    pool = _pool(3)
    first = await pool.acquire(frozenset())
    assert first is not None
    await pool.mark_failed(first.slot, disable=False)
    second = await pool.acquire(frozenset({first.slot}))
    assert second is not None
    await pool.mark_succeeded(second.slot)

    current = await pool.acquire(frozenset())

    assert current is not None
    assert current.slot == second.slot


@pytest.mark.asyncio
async def test_late_success_does_not_reactivate_disabled_slot() -> None:
    pool = _pool(2)
    lease = await pool.acquire(frozenset())
    assert lease is not None

    await pool.mark_failed(lease.slot, disable=True)
    await pool.mark_succeeded(lease.slot)

    assert await pool.state(lease.slot) is LlmKeyState.DISABLED_FOR_PROCESS
    replacement = await pool.acquire(frozenset())
    assert replacement is not None
    assert replacement.slot != lease.slot


@pytest.mark.asyncio
async def test_concurrent_pool_updates_do_not_corrupt_index() -> None:
    pool = _pool(5)

    async def rotate_once() -> int:
        lease = await pool.acquire(frozenset())
        assert lease is not None
        await pool.mark_failed(lease.slot, disable=False)
        return lease.slot

    slots = await asyncio.gather(*(rotate_once() for _ in range(50)))
    current = await pool.acquire(frozenset())

    assert all(0 <= slot < 5 for slot in slots)
    assert current is not None
    assert 0 <= current.slot < 5
