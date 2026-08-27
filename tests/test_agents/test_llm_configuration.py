"""Unit test parse, validation và migration precedence của LLM key list."""

from collections.abc import Mapping

import pytest
from config import Settings
from pydantic import ValidationError
from src.infrastructure.llm.runtime_configuration import effective_api_keys, resolve_runtime_configuration


def _settings(overrides: Mapping[str, object] | None = None) -> Settings:
    values: dict[str, object] = {
        "app_name": "Test",
        "app_env": "test",
        "app_host": "127.0.0.1",
        "app_port": 8000,
        "debug": False,
        "postgres_user": "u",
        "postgres_password": "p",
        "postgres_host": "h",
        "postgres_port": 5432,
        "postgres_db": "d",
        "redis_host": "r",
        "redis_port": 6379,
        "redis_db": 0,
        "secret_key": "s",
        "jwt_algorithm": "HS256",
        "access_token_expire_minutes": 30,
        "llm_provider": "openai",
        "model_name": "gpt-test",
        "llm_temperature": 0.0,
        "log_level": "INFO",
        "langchain_tracing_v2": False,
        "langchain_project": "p",
        "cors_origins": "*",
    }
    values.update(overrides or {})
    return Settings(_env_file=None, **values)


def _raw_keys(settings: Settings) -> tuple[str, ...]:
    return tuple(key.get_secret_value() for key in effective_api_keys(settings))


@pytest.mark.parametrize("count", [1, 2, 5])
def test_dynamic_key_count_requires_no_code_change(count: int) -> None:
    keys = [f" key-{index} " for index in range(count)]

    settings = _settings({"llm_api_keys": keys})

    assert _raw_keys(settings) == tuple(f"key-{index}" for index in range(count))


def test_new_key_list_has_priority_over_legacy_keys() -> None:
    settings = _settings(
        {
            "llm_api_keys": ["new-1", "new-2"],
            "llm_api_key": "legacy",
            "openai_api_key": "provider-legacy",
        }
    )

    assert _raw_keys(settings) == ("new-1", "new-2")


def test_legacy_key_precedence_is_preserved() -> None:
    direct = _settings({"llm_api_key": "generic", "openai_api_key": "provider"})
    provider = _settings({"openai_api_key": "provider"})

    assert _raw_keys(direct) == ("generic",)
    assert _raw_keys(provider) == ("provider",)


@pytest.mark.parametrize("keys", [[], [""], ["same", " same "]])
def test_empty_blank_or_duplicate_key_list_fails(keys: list[str]) -> None:
    with pytest.raises(ValidationError):
        _settings({"llm_api_keys": keys})


def test_json_environment_is_parsed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_API_KEYS", '["env-1", " env-2 "]')

    assert _raw_keys(_settings()) == ("env-1", "env-2")


def test_blank_environment_fails_without_legacy_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_API_KEYS", "")
    monkeypatch.setenv("LLM_API_KEY", "legacy-must-not-win")

    with pytest.raises(ValidationError):
        _settings()


def test_settings_representation_masks_new_keys() -> None:
    rendered = repr(_settings({"llm_api_keys": ["never-print-this"]}))

    assert "never-print-this" not in rendered


def test_multi_provider_priority_and_models_follow_configuration() -> None:
    settings = _settings(
        {
            "llm_provider_priority": ["GEMINI", "OPENAI"],
            "gemini_api_keys": ["explicit-gemini"],
            "openai_api_keys": ["explicit-openai"],
            "gemini_model": "gemini-test",
            "openai_model": "openai-test",
        }
    )

    runtime = resolve_runtime_configuration(settings)

    assert [item.provider.value for item in runtime.candidates] == ["GEMINI", "OPENAI"]
    assert [item.model_name for item in runtime.candidates] == ["gemini-test", "openai-test"]


def test_generic_credentials_are_detected_by_longest_prefix() -> None:
    settings = _settings(
        {
            "llm_provider_priority": ["ANTHROPIC", "OPENAI", "GEMINI"],
            "llm_api_keys": ["sk-ant-test", "sk-or-v1-test", "AIza-test"],
            "anthropic_model": "claude-test",
            "openai_model": "openai/test",
            "gemini_model": "gemini-test",
        }
    )

    runtime = resolve_runtime_configuration(settings)

    counts = {item.provider.value: len(item.api_keys) for item in runtime.candidates}
    assert counts == {"ANTHROPIC": 1, "OPENAI": 1, "GEMINI": 1}


def test_explicit_provider_binding_overrides_key_prefix() -> None:
    settings = _settings(
        {
            "llm_provider_priority": ["GEMINI"],
            "gemini_api_keys": ["sk-prefix-must-not-win"],
            "gemini_model": "gemini-test",
        }
    )

    runtime = resolve_runtime_configuration(settings)

    assert runtime.candidates[0].provider.value == "GEMINI"


def test_unknown_generic_credential_fails_without_exposing_value() -> None:
    settings = _settings(
        {
            "llm_provider_priority": ["OPENAI"],
            "llm_api_keys": ["unknown-never-expose"],
            "openai_model": "openai-test",
        }
    )

    with pytest.raises(ValueError) as raised:
        resolve_runtime_configuration(settings)

    assert "unknown-never-expose" not in str(raised.value)
