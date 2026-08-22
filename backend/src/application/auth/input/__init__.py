"""Public input models của application service Authentication."""

from dataclasses import dataclass

from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class ResolveCurrentActorInput:
    """Danh tính MVP cần được resolve thành actor hiện tại."""

    user_id: EntityID
    username: str
    email: str


__all__ = ["ResolveCurrentActorInput"]
