"""Apply classified LLM failures vào credential/provider state."""

from typing import Protocol

from src.infrastructure.llm.credential_pool import CredentialPool
from src.infrastructure.llm.exception_translator import translate_llm_failure
from src.infrastructure.llm.failure_classifier import LlmFailureAction, LlmFailureClassifier
from src.infrastructure.llm.gateway_observability import (
    GatewayLogContext,
    log_failure,
    log_provider_cooldown,
    log_rotated,
)
from src.infrastructure.llm.provider_health import ProviderHealthRegistry
from src.infrastructure.llm.runtime_configuration import ProviderRuntimeConfiguration


class _FailureRoute(Protocol):
    configuration: ProviderRuntimeConfiguration
    credential_pool: CredentialPool


class GatewayFailureHandler:
    """Tách state transition do failure khỏi provider routing loop."""

    def __init__(self, health: ProviderHealthRegistry) -> None:
        self._health = health
        self._classifier = LlmFailureClassifier()

    async def handle(
        self,
        route: _FailureRoute,
        key_id: str,
        exc: Exception,
    ) -> bool:
        """Apply failure và trả True khi phải fallback provider."""
        decision = self._classifier.classify(exc)
        context = _log_context(route.configuration)
        log_failure(context, key_id, decision.reason)
        if decision.action is LlmFailureAction.FAIL:
            raise translate_llm_failure(decision) from exc
        if decision.action is LlmFailureAction.ROTATE:
            await route.credential_pool.mark_rate_limited(key_id)
            log_rotated(context, key_id, decision.reason)
            return False
        if decision.action is LlmFailureAction.DISABLE_AND_ROTATE:
            await route.credential_pool.disable(key_id)
            log_rotated(context, key_id, decision.reason)
            return False
        cooled = await self._health.mark_failed(route.configuration.provider)
        if cooled:
            log_provider_cooldown(context, decision.reason)
        return True


def _log_context(configuration: ProviderRuntimeConfiguration) -> GatewayLogContext:
    return GatewayLogContext(configuration.provider.value, configuration.model_name)
