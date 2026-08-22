"""Unit tests cho provider registry và lazy chat model."""

from typing import cast

import pytest
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from src.common.exceptions.infrastructure import InfrastructureException
from src.infrastructure.llm import factory
from src.infrastructure.llm.lazy_chat_model import LazyChatModel
from src.infrastructure.llm.provider_registry import (
    ChatModelConfiguration,
    ChatModelProviderRegistry,
    create_default_provider_registry,
)


def _configuration(provider: str, base_url: str = "") -> ChatModelConfiguration:
    """Tạo cấu hình tối thiểu không thực hiện network call."""
    return ChatModelConfiguration(provider, "test-model", "test-key", base_url, 0.0, 100, 5.0)


@pytest.mark.parametrize("provider", ["openai", "openai_compatible"])
def test_openai_providers_disable_sdk_retry(provider: str) -> None:
    """OpenAI và compatible dùng cùng adapter với automatic retry bằng không."""
    model = create_default_provider_registry().build(
        _configuration(provider, "http://localhost:11434/v1")
    )

    assert isinstance(model, ChatOpenAI)
    assert model.max_retries == 0


def test_google_provider_builds_async_capable_chat_model() -> None:
    """Google registry tạo integration LangChain chính thức và tắt retry."""
    model = create_default_provider_registry().build(_configuration("google"))

    assert isinstance(model, ChatGoogleGenerativeAI)
    assert model.max_retries == 0


def test_custom_provider_registration_requires_no_core_change() -> None:
    """Builder tùy chỉnh được resolve chỉ bằng registry registration."""
    registry = ChatModelProviderRegistry()
    sentinel = cast(BaseChatModel, object())
    registry.register("custom", lambda configuration: sentinel)

    assert registry.build(_configuration("CUSTOM")) is sentinel


def test_unknown_provider_fails_with_infrastructure_error() -> None:
    """Provider chưa đăng ký không làm lộ KeyError khỏi Infrastructure."""
    with pytest.raises(InfrastructureException):
        ChatModelProviderRegistry().build(_configuration("missing"))


def test_lazy_chat_model_builds_once_per_process_resource() -> None:
    """Lazy wrapper chỉ gọi builder ở lần sử dụng đầu tiên."""
    calls = 0
    sentinel = cast(BaseChatModel, object())

    def builder() -> BaseChatModel:
        nonlocal calls
        calls += 1
        return sentinel

    lazy = LazyChatModel(builder)

    assert lazy.get() is sentinel
    assert lazy.get() is sentinel
    assert calls == 1


def test_default_model_factory_is_cached_per_process(monkeypatch: pytest.MonkeyPatch) -> None:
    """Composition factory không dựng lại model cho từng request."""
    calls = 0
    sentinel = cast(BaseChatModel, object())

    def builder() -> BaseChatModel:
        nonlocal calls
        calls += 1
        return sentinel

    factory.get_cached_chat_model.cache_clear()
    monkeypatch.setattr(factory, "build_chat_model", builder)

    assert factory.get_cached_chat_model() is sentinel
    assert factory.get_cached_chat_model() is sentinel
    assert calls == 1
    factory.get_cached_chat_model.cache_clear()


def test_auto_provider_detects_google_when_gemini_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tự động chọn Google khi cấu hình LLM_PROVIDER=auto và model là Gemini."""
    from config import Settings

    settings = Settings(
        app_name="Test", app_env="test", app_host="127.0.0.1", app_port=8000, debug=True,
        postgres_user="u", postgres_password="p", postgres_host="h", postgres_port=5432, postgres_db="d",
        redis_host="r", redis_port=6379, secret_key="s", jwt_algorithm="HS256", access_token_expire_minutes=30,
        llm_provider="auto", model_name="gemini-1.5-flash", google_api_key="test-key",
        llm_temperature=0.0, log_level="INFO", langchain_tracing_v2=False, langchain_project="p", cors_origins="*",
    )
    model = factory.build_chat_model(settings)
    assert isinstance(model, ChatGoogleGenerativeAI)
