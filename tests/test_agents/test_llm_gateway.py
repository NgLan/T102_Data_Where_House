"""Unit tests cho multi-provider routing và failure boundaries."""

import logging
from typing import cast

import pytest
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, SecretStr
from src.common.exceptions.infrastructure import InfrastructureException
from src.infrastructure.llm.api_credential import ApiCredential, CredentialStatus
from src.infrastructure.llm.credential_pool import CredentialPool
from src.infrastructure.llm.llm_gateway import (
    LlmGateway,
    LlmGatewayResources,
    ProviderGatewayRoute,
)
from src.infrastructure.llm.provider_health import ProviderHealthRegistry, ProviderStatus
from src.infrastructure.llm.provider_routing_policy import ProviderRoutingPolicy
from src.infrastructure.llm.provider_types import LlmProvider
from src.infrastructure.llm.runtime_configuration import ProviderRuntimeConfiguration


class SampleOutput(BaseModel):
    """Structured result tối thiểu cho fake client."""

    value: str


class FakeClient:
    """Fake provider client phát kết quả theo script."""

    def __init__(self, results: list[object]) -> None:
        self.results = results
        self.calls = 0

    def with_structured_output(
        self,
        _schema: type[BaseModel],
        *,
        include_raw: bool = False,
    ) -> "FakeClient":
        return self

    async def ainvoke(self, _messages: list[object]) -> BaseModel:
        self.calls += 1
        result = self.results.pop(0)
        if isinstance(result, Exception):
            raise result
        return cast(BaseModel, result)


class FakeRawResponse:
    """Raw response chỉ chứa metadata an toàn cho observability test."""

    response_metadata = {"finish_reason": "stop"}
    usage_metadata = {"input_tokens": 11, "output_tokens": 7, "total_tokens": 18}


def _route(
    provider: LlmProvider,
    scripts: list[list[object]],
    model: str = "test-model",
) -> tuple[ProviderGatewayRoute, CredentialPool, list[FakeClient]]:
    keys = tuple(SecretStr(f"never-log-{provider.value}-{index}") for index in range(len(scripts)))
    credentials = tuple(
        ApiCredential(f"{provider.value.casefold()}_{index:02d}", provider, key)
        for index, key in enumerate(keys, start=1)
    )
    pool = CredentialPool(credentials, 60.0)
    clients = [FakeClient(script) for script in scripts]
    configuration = ProviderRuntimeConfiguration(provider, model, keys, "")
    mapped = {credential.key_id: cast(BaseChatModel, client) for credential, client in zip(credentials, clients)}
    return ProviderGatewayRoute(configuration, mapped, pool), pool, clients


def _gateway(routes: tuple[ProviderGatewayRoute, ...], threshold: int = 2) -> LlmGateway:
    providers = tuple(route.configuration.provider for route in routes)
    health = ProviderHealthRegistry(providers, (threshold, 30.0))
    return LlmGateway(LlmGatewayResources(ProviderRoutingPolicy(routes), health))


@pytest.mark.asyncio
async def test_rate_limit_rotates_key_inside_same_provider() -> None:
    route, pool, clients = _route(
        LlmProvider.OPENAI,
        [[RuntimeError("rate limit")], [SampleOutput(value="second")]],
    )

    result = await _gateway((route,)).with_structured_output(SampleOutput).ainvoke([])

    assert cast(SampleOutput, result).value == "second"
    assert clients[0].calls == clients[1].calls == 1
    assert await pool.status("openai_01") is CredentialStatus.COOLDOWN


@pytest.mark.asyncio
async def test_authentication_disables_key_then_uses_next_key() -> None:
    route, pool, _clients = _route(
        LlmProvider.OPENAI,
        [[RuntimeError("invalid api key")], [SampleOutput(value="replacement")]],
    )

    await _gateway((route,)).with_structured_output(SampleOutput).ainvoke([])

    assert await pool.status("openai_01") is CredentialStatus.DISABLED


@pytest.mark.asyncio
async def test_provider_outage_falls_back_without_rotating_other_keys() -> None:
    first, first_pool, first_clients = _route(
        LlmProvider.OPENAI,
        [[RuntimeError("service unavailable")], [SampleOutput(value="must-not-run")]],
    )
    second, _pool, _clients = _route(LlmProvider.GEMINI, [[SampleOutput(value="fallback")]])

    result = await _gateway((first, second)).with_structured_output(SampleOutput).ainvoke([])

    assert cast(SampleOutput, result).value == "fallback"
    assert first_clients[1].calls == 0
    assert await first_pool.status("openai_01") is CredentialStatus.AVAILABLE


@pytest.mark.asyncio
async def test_structured_validation_failure_does_not_change_credential() -> None:
    route, pool, _clients = _route(LlmProvider.OPENAI, [[ValueError("validation error")]])

    with pytest.raises(InfrastructureException):
        await _gateway((route,)).with_structured_output(SampleOutput).ainvoke([])

    assert await pool.status("openai_01") is CredentialStatus.AVAILABLE


@pytest.mark.asyncio
async def test_model_not_found_fails_without_provider_fallback() -> None:
    first, pool, _clients = _route(LlmProvider.OPENAI, [[RuntimeError("404 model not found")]])
    second, _pool2, clients = _route(LlmProvider.GEMINI, [[SampleOutput(value="must-not-run")]])

    with pytest.raises(InfrastructureException):
        await _gateway((first, second)).with_structured_output(SampleOutput).ainvoke([])

    assert clients[0].calls == 0
    assert await pool.status("openai_01") is CredentialStatus.AVAILABLE


@pytest.mark.asyncio
async def test_repeated_provider_outage_enters_cooldown() -> None:
    first, _pool, _clients = _route(
        LlmProvider.OPENAI,
        [[RuntimeError("service unavailable"), RuntimeError("service unavailable")]],
    )
    second, _pool2, _clients2 = _route(
        LlmProvider.GEMINI,
        [[SampleOutput(value="one"), SampleOutput(value="two")]],
    )
    health = ProviderHealthRegistry((LlmProvider.OPENAI, LlmProvider.GEMINI), (2, 30.0))
    routing = ProviderRoutingPolicy((first, second))
    gateway = LlmGateway(LlmGatewayResources(routing, health))

    await gateway.with_structured_output(SampleOutput).ainvoke([])
    await gateway.with_structured_output(SampleOutput).ainvoke([])

    assert await health.status(LlmProvider.OPENAI) is ProviderStatus.COOLDOWN


@pytest.mark.asyncio
async def test_provider_success_resets_consecutive_failure_counter() -> None:
    provider = LlmProvider.OPENAI
    health = ProviderHealthRegistry((provider,), (2, 30.0))

    assert await health.mark_failed(provider) is False
    await health.mark_succeeded(provider)
    assert await health.mark_failed(provider) is False
    assert await health.status(provider) is ProviderStatus.AVAILABLE


@pytest.mark.asyncio
async def test_logs_record_route_metadata_without_secret(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)
    first, _pool, _clients = _route(LlmProvider.OPENAI, [[RuntimeError("service unavailable")]], "gpt-test")
    second, _pool2, _clients2 = _route(LlmProvider.GEMINI, [[SampleOutput(value="ok")]], "gemini-test")

    await _gateway((first, second)).with_structured_output(SampleOutput).ainvoke([])

    rendered = " ".join(str(record.__dict__) for record in caplog.records)
    assert "never-log-" not in rendered
    assert "OPENAI" in rendered and "GEMINI" in rendered
    assert "gpt-test" in rendered and "gemini-test" in rendered


@pytest.mark.asyncio
async def test_completion_log_records_route_and_usage_metadata(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO)
    response = {"raw": FakeRawResponse(), "parsed": SampleOutput(value="ok")}
    route, _pool, _clients = _route(LlmProvider.OPENAI, [[response]], "gpt-observed")

    await _gateway((route,)).with_structured_output(SampleOutput, include_raw=True).ainvoke([])

    completed = next(record for record in caplog.records if record.__dict__.get("event") == "llm_call_completed")
    assert completed.__dict__["provider"] == "OPENAI"
    assert completed.__dict__["model"] == "gpt-observed"
    assert completed.__dict__["finish_reason"] == "stop"
    assert completed.__dict__["usage"]["total"] == 18


@pytest.mark.asyncio
async def test_all_providers_fail_with_standard_infrastructure_exception() -> None:
    first, _pool, _clients = _route(LlmProvider.OPENAI, [[RuntimeError("service unavailable")]])
    second, _pool2, _clients2 = _route(LlmProvider.GEMINI, [[TimeoutError("timeout")]])

    with pytest.raises(InfrastructureException) as raised:
        await _gateway((first, second)).with_structured_output(SampleOutput).ainvoke([])

    assert raised.value.__cause__ is not None
