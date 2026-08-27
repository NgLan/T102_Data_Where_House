"""Runtime credential model chỉ tồn tại trong Infrastructure."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from pydantic import SecretStr
from src.infrastructure.llm.provider_types import LlmProvider


class CredentialStatus(StrEnum):
    """Trạng thái credential trong process hiện tại."""

    AVAILABLE = "AVAILABLE"
    COOLDOWN = "COOLDOWN"
    DISABLED = "DISABLED"


@dataclass(slots=True)
class ApiCredential:
    """Credential mutable được bảo vệ bởi lock của provider pool."""

    key_id: str
    provider: LlmProvider
    secret: SecretStr
    status: CredentialStatus = CredentialStatus.AVAILABLE
    cooldown_until: datetime | None = None
    consecutive_failures: int = 0


@dataclass(frozen=True, slots=True)
class CredentialLease:
    """Credential được cấp cho một provider attempt."""

    key_id: str
    secret: SecretStr

