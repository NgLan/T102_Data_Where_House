"""Provider-neutral client configuration cho registry/adapters."""

from dataclasses import dataclass

from pydantic import SecretStr


@dataclass(frozen=True, slots=True)
class ChatModelConfiguration:
    """Cấu hình provider-neutral cho một chat model client."""

    provider: str
    model_name: str
    api_key: SecretStr
    base_url: str
    temperature: float
    max_tokens: int
    timeout_seconds: float
