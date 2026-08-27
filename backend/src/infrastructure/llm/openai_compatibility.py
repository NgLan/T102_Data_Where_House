"""OpenRouter/OpenAI-compatible configuration normalization."""

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def resolve_provider_config(api_key: str, base_url: str, model_name: str) -> tuple[str, str]:
    """Giữ tương thích OpenRouter mà không đoán provider/model business routing."""
    resolved_url = base_url.strip().rstrip("/")
    if not resolved_url and api_key.casefold().startswith("sk-or-v1-"):
        resolved_url = OPENROUTER_BASE_URL
    resolved_model = model_name.strip()
    openai_prefixes = ("gpt-", "chatgpt-", "o1", "o3", "o4")
    if resolved_url.casefold() == OPENROUTER_BASE_URL.casefold():
        if "/" not in resolved_model and resolved_model.startswith(openai_prefixes):
            resolved_model = f"openai/{resolved_model}"
    return resolved_url, resolved_model


def is_local_endpoint(base_url: str) -> bool:
    """Nhận diện endpoint local cho migration guidance."""
    normalized = base_url.casefold()
    return "localhost" in normalized or "127.0.0.1" in normalized
