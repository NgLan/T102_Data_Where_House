"""Public output models của application service Authentication."""

from dataclasses import dataclass
from datetime import datetime

from src.domain.shared.types import EntityID
from src.domain.user.entities import User


@dataclass(frozen=True, slots=True)
class CurrentActorOutput:
    """Danh tính tối thiểu được phép đi qua application boundary."""

    id: EntityID
    username: str
    email: str
    full_name: str | None
    is_active: bool
    created_at: datetime

    @classmethod
    def from_domain(cls, user: User) -> "CurrentActorOutput":
        """Ánh xạ User entity sang actor output."""
        return cls(
            id=user.id,
            username=user.username,
            email=user.email.value,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
        )


@dataclass(frozen=True, slots=True)
class AuthSessionOutput:
    """User và JWT chỉ dùng tại presentation boundary để đặt cookie."""

    access_token: str
    expires_at: datetime
    user: CurrentActorOutput


__all__ = ["AuthSessionOutput", "CurrentActorOutput"]
