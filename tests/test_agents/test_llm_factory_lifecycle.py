"""Unit test client và shared key-pool lifecycle tại composition factory."""

from typing import cast

import pytest
from config import Settings
from langchain_core.language_models import BaseChatModel
from pydantic import SecretStr
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.infrastructure.llm import factory
from src.infrastructure.llm.gateway_builder import GatewaySharedState
from src.infrastructure.llm.lazy_chat_model import ILLMGateway
from src.infrastructure.llm.provider_registry import ChatModelConfiguration, ChatModelProviderRegistry
from src.infrastructure.llm.runtime_configuration import LlmRuntimeConfiguration
from src.presentation.dependencies import llm as llm_dependencies


def _settings() -> Settings:
    return Settings.model_construct(
        llm_provider="openai",
        llm_api_keys=(SecretStr("key-1"), SecretStr("key-2")),
        llm_api_key="",
        openai_api_key="",
        google_api_key="",
        llm_base_url="",
        openai_base_url="",
        model_name="gpt-test",
        llm_temperature=0.0,
        agent_max_output_tokens=100,
        llm_request_timeout_seconds=5.0,
        conversation_summary_model_name="gpt-summary",
        conversation_summary_temperature=0.0,
        conversation_summary_max_output_tokens=50,
    )


def test_factory_builds_and_reuses_one_client_per_key() -> None:
    registry = ChatModelProviderRegistry()
    clients: list[BaseChatModel] = []

    def build(_configuration: ChatModelConfiguration) -> BaseChatModel:
        client = cast(BaseChatModel, object())
        clients.append(client)
        return client

    registry.register("openai", build)

    factory.build_chat_model(_settings(), registry)

    assert len(clients) == 2


def test_local_endpoint_requires_explicit_placeholder_credential() -> None:
    settings = _settings().model_copy(
        update={"llm_api_keys": None, "llm_base_url": "http://localhost:11434/v1"}
    )
    registry = ChatModelProviderRegistry()
    configured_keys: list[str] = []

    def build(configuration: ChatModelConfiguration) -> BaseChatModel:
        configured_keys.append(configuration.api_key.get_secret_value())
        return cast(BaseChatModel, object())

    registry.register("openai", build)

    with pytest.raises(InfrastructureException):
        factory.build_chat_model(settings, registry)

    assert configured_keys == []


def test_cloud_provider_without_any_key_fails_clearly() -> None:
    settings = _settings().model_copy(update={"llm_api_keys": None})

    with pytest.raises(InfrastructureException) as raised:
        factory.build_chat_model(settings)

    assert raised.value.code is ErrorCode.LLM_ERROR


def test_startup_rejects_configured_provider_without_registered_adapter() -> None:
    settings = _settings().model_copy(
        update={
            "llm_provider_priority": ("ANTHROPIC",),
            "llm_api_keys": None,
            "anthropic_api_keys": (SecretStr("sk-ant-test"),),
            "anthropic_model_name": "claude-test",
        }
    )
    registry = ChatModelProviderRegistry()
    registry.register("openai", lambda _configuration: cast(BaseChatModel, object()))

    with pytest.raises(InfrastructureException) as raised:
        factory.build_chat_model(settings, registry)

    assert raised.value.code is ErrorCode.LLM_ERROR


def test_main_and_summary_models_share_process_key_pool(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _settings()
    pools: list[GatewaySharedState] = []
    sentinel = cast(ILLMGateway, object())

    def build(
        _runtime: LlmRuntimeConfiguration,
        _registry: ChatModelProviderRegistry,
        pool: GatewaySharedState,
    ) -> ILLMGateway:
        pools.append(pool)
        return sentinel

    monkeypatch.setattr(llm_dependencies, "get_settings", lambda: settings)
    monkeypatch.setattr(factory, "_build_gateway", build)
    llm_dependencies.get_gateway_state.cache_clear()
    llm_dependencies.get_llm_gateway.cache_clear()
    llm_dependencies.get_summary_llm_gateway.cache_clear()

    llm_dependencies.get_llm_gateway()
    llm_dependencies.get_summary_llm_gateway()

    assert pools[0] is pools[1]
    llm_dependencies.get_gateway_state.cache_clear()
    llm_dependencies.get_llm_gateway.cache_clear()
    llm_dependencies.get_summary_llm_gateway.cache_clear()
