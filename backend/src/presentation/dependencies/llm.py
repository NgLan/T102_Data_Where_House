"""Composition root và process cache cho LLM Gateway profiles."""

from functools import lru_cache

from config import get_settings
from src.infrastructure.llm.factory import (
    build_chat_model,
    build_gateway_state,
    build_summary_chat_model,
)
from src.infrastructure.llm.gateway_builder import GatewaySharedState
from src.infrastructure.llm.lazy_chat_model import ILLMGateway


@lru_cache
def get_gateway_state() -> GatewaySharedState:
    """Cache provider-scoped credential pools/health theo process."""
    return build_gateway_state(get_settings())


@lru_cache
def get_llm_gateway() -> ILLMGateway:
    """Cache default logical LLM Gateway profile."""
    return build_chat_model(get_settings(), shared_state=get_gateway_state())


@lru_cache
def get_summary_llm_gateway() -> ILLMGateway:
    """Cache summary profile dùng chung provider runtime state."""
    return build_summary_chat_model(get_settings(), shared_state=get_gateway_state())


def initialize_llm_gateway() -> None:
    """Fail-fast default và summary provider/model configuration lúc startup."""
    get_llm_gateway()
    get_summary_llm_gateway()
