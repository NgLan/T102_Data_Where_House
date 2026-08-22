"""Public output models của application service Authentication."""

from dataclasses import dataclass

from src.domain.shared.types import EntityID
from src.domain.user.entities import User


@dataclass(frozen=True, slots=True)
class CurrentActorOutput:
    """Danh tính tối thiểu được phép đi qua application boundary."""

    id: EntityID
    username: str
    email: str

    @classmethod
    def from_domain(cls, user: User) -> "CurrentActorOutput":
        """Ánh xạ User entity sang actor output."""
        return cls(id=user.id, username=user.username, email=user.email.value)


__all__ = ["CurrentActorOutput"]
