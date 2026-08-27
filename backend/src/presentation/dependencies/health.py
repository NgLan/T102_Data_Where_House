"""Composition root cho Health service."""

from config import get_settings
from src.application.health.health_service import HealthService
from src.application.health.i_health_service import IHealthService
from src.infrastructure.database.config import get_async_db_engine
from src.infrastructure.health.sqlalchemy_health_probe import SqlAlchemyHealthProbe
from src.infrastructure.llm.gateway_builder import GatewaySharedState
from src.infrastructure.llm.runtime_configuration import LlmRuntimeConfiguration, resolve_runtime_configuration
from src.presentation.dependencies.llm import get_gateway_state


async def get_health_service() -> IHealthService:
    """Dựng health service từ runtime state mà không expose credential."""
    settings = get_settings()
    runtime = resolve_runtime_configuration(settings)
    configured = await _has_usable_route(runtime, get_gateway_state())
    return HealthService(
        SqlAlchemyHealthProbe(get_async_db_engine()),
        settings.app_env,
        "1.0.0",
        runtime.provider,
        runtime.model_name,
        configured,
    )


async def _has_usable_route(
    runtime: LlmRuntimeConfiguration,
    state: GatewaySharedState,
) -> bool:
    for candidate in runtime.candidates:
        provider = candidate.provider
        if await state.health.is_available(provider) and await state.pools[provider].has_available():
            return True
    return False

