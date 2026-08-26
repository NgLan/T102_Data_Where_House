"""Unit test key failover minh bạch tại structured chat model boundary."""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import cast

import pytest
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, SecretStr
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.infrastructure.llm.api_key_pool import LlmApiKeyPool
from src.infrastructure.llm.rotating_chat_model import RotatingChatModel, RotatingChatModelResources


class SampleOutput(BaseModel):
    """Structured result tối thiểu cho fake provider."""

    value: str


class FakeClient:
    """Provider client ghi số lần gọi và phát scripted result."""

    def __init__(self, results: list[object]) -> None:
        self.results = results
        self.calls = 0

    def with_structured_output(self, _schema: type[BaseModel]) -> "FakeClient":
        return self

    async def ainvoke(self, _messages: list[object]) -> BaseModel:
        self.calls += 1
        result = self.results.pop(0)
        if isinstance(result, Exception):
            raise result
        if callable(result):
            return await cast(Callable[[], Awaitable[BaseModel]], result)()
        return cast(BaseModel, result)


def _model(scripted: list[list[object]]) -> tuple[RotatingChatModel, list[FakeClient]]:
    clients = [FakeClient(results) for results in scripted]
    keys = tuple(SecretStr(f"secret-{slot}") for slot in range(len(clients)))
    pool = LlmApiKeyPool(keys)
    resources = RotatingChatModelResources(
        cast(tuple[BaseChatModel, ...], tuple(clients)), pool, "openai"
    )
    return RotatingChatModel(resources), clients


async def _invoke(model: RotatingChatModel) -> SampleOutput:
    result = await model.with_structured_output(SampleOutput).ainvoke([])
    return cast(SampleOutput, result)


@pytest.mark.asyncio
async def test_single_key_success_calls_provider_once() -> None:
    model, clients = _model([[SampleOutput(value="K1")]])

    assert await _invoke(model) == SampleOutput(value="K1")
    assert clients[0].calls == 1


@pytest.mark.asyncio
async def test_quota_and_rate_limit_rotate_until_success() -> None:
    model, clients = _model(
        [
            [RuntimeError("insufficient_quota")],
            [RuntimeError("rate limit")],
            [SampleOutput(value="K3")],
        ]
    )

    assert await _invoke(model) == SampleOutput(value="K3")
    assert [client.calls for client in clients] == [1, 1, 1]


@pytest.mark.asyncio
async def test_successful_backup_becomes_current_slot() -> None:
    model, clients = _model(
        [
            [RuntimeError("insufficient_quota")],
            [SampleOutput(value="first"), SampleOutput(value="second")],
        ]
    )

    assert (await _invoke(model)).value == "first"
    assert (await _invoke(model)).value == "second"
    assert [client.calls for client in clients] == [1, 2]


@pytest.mark.asyncio
async def test_all_keys_exhausted_without_repeating_slot() -> None:
    model, clients = _model(
        [[RuntimeError("quota_exceeded")], [RuntimeError("rate limit")], [RuntimeError("invalid api key")]]
    )

    with pytest.raises(InfrastructureException) as raised:
        await _invoke(model)

    assert raised.value.code is ErrorCode.LLM_CREDENTIALS_EXHAUSTED
    assert [client.calls for client in clients] == [1, 1, 1]


@pytest.mark.asyncio
async def test_invalid_request_fails_without_trying_backup() -> None:
    model, clients = _model([[ValueError("invalid request")], [SampleOutput(value="must-not-run")]])

    with pytest.raises(InfrastructureException) as raised:
        await _invoke(model)

    assert raised.value.code is ErrorCode.LLM_ERROR
    assert [client.calls for client in clients] == [1, 0]


@pytest.mark.asyncio
async def test_network_calls_are_not_serialized_by_pool_lock() -> None:
    entered = 0
    both_entered = asyncio.Event()

    async def concurrent_result() -> BaseModel:
        nonlocal entered
        entered += 1
        if entered == 2:
            both_entered.set()
        await asyncio.wait_for(both_entered.wait(), timeout=1)
        return SampleOutput(value="ok")

    model, clients = _model([[concurrent_result, concurrent_result]])

    results = await asyncio.wait_for(asyncio.gather(_invoke(model), _invoke(model)), timeout=2)

    assert [result.value for result in results] == ["ok", "ok"]
    assert clients[0].calls == 2


@pytest.mark.asyncio
async def test_logs_and_error_do_not_contain_secret(caplog: pytest.LogCaptureFixture) -> None:
    secret = "sk-never-log-this"
    model, _ = _model([[RuntimeError(f"insufficient_quota api_key={secret}")]])
    caplog.set_level(logging.INFO)

    with pytest.raises(InfrastructureException) as raised:
        await _invoke(model)

    disabled = next(record for record in caplog.records if record.event == "llm_key_disabled")
    assert disabled.llm_key_slot == 0
    assert secret not in caplog.text
    assert secret not in str(raised.value)
