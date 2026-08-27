"""Deterministic short references dùng riêng tại RequirementAgent boundary."""

from dataclasses import dataclass

from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class TransportReferenceMap:
    """Ánh xạ hai chiều giữa transport ref và canonical entity ID."""

    by_reference: dict[str, EntityID]
    by_id: dict[EntityID, str]

    @classmethod
    def create(
        cls,
        prefix: str,
        identifiers: tuple[EntityID, ...],
    ) -> "TransportReferenceMap":
        """Sinh ref ổn định theo thứ tự canonical input."""
        by_reference = {f"{prefix}{index}": identifier for index, identifier in enumerate(identifiers, start=1)}
        return cls(by_reference, {value: key for key, value in by_reference.items()})

    @property
    def references(self) -> tuple[str, ...]:
        """Trả refs theo thứ tự đã tạo."""
        return tuple(self.by_reference)

    def resolve(self, reference: str) -> EntityID | None:
        """Resolve exact ref; không fuzzy hoặc positional fallback."""
        return self.by_reference.get(reference)

    def reference_for(self, identifier: EntityID) -> str | None:
        """Lấy ref của canonical ID nếu thuộc invocation."""
        return self.by_id.get(identifier)


@dataclass(frozen=True, slots=True)
class SourceCoverageReferenceBoundary:
    """Ba namespace reference dùng trong đúng một Source Coverage invocation."""

    requirements: TransportReferenceMap
    analytical_requirements: TransportReferenceMap
    sources: TransportReferenceMap
