"""Candidate mapping và source reference của Source Confirmation."""

from dataclasses import dataclass, field

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.analytical_requirement.enums import SourceCandidateKind
from src.domain.shared.enum_rules import normalize_str_enum
from src.domain.shared.types import EntityID
from src.domain.shared.value_object import BaseValueObject


@dataclass(frozen=True)
class SourceCoverageReference(BaseValueObject):
    """Reference chính xác tới một column hoặc relationship có thật."""

    kind: SourceCandidateKind
    source_id: EntityID
    role_key: str | None = None
    role_label: str | None = None
    table_name: str | None = None
    column_name: str | None = None
    from_column: str | None = None
    to_column: str | None = None

    def __post_init__(self) -> None:
        kind = normalize_str_enum(self.kind, SourceCandidateKind, ErrorCode.VALIDATION_ERROR)
        role_key = self.role_key.strip() if self.role_key else None
        role_label = self.role_label.strip() if self.role_label else None
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "role_key", role_key)
        object.__setattr__(self, "role_label", role_label)
        if bool(role_key) != bool(role_label) or not _is_role_key(role_key) or not _has_valid_shape(self):
            raise BusinessException(
                ErrorCode.VALIDATION_ERROR,
                "Source coverage reference không đúng shape hoặc role.",
            )

    def identity(self) -> tuple[object, ...]:
        """Trả identity vật lý và role để phát hiện reference trùng."""
        return (
            self.kind,
            self.source_id,
            self.table_name,
            self.column_name,
            self.from_column,
            self.to_column,
        )


@dataclass(frozen=True)
class SourceCoverageCandidate(BaseValueObject):
    """Một câu trả lời hoàn chỉnh gồm business label và source evidence."""

    id: EntityID
    label: str
    references: tuple[SourceCoverageReference, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        label = self.label.strip()
        references = tuple(self.references)
        identities = [item.identity() for item in references]
        if not label or not references or len(identities) != len(set(identities)):
            raise BusinessException(
                ErrorCode.VALIDATION_ERROR,
                "Candidate mapping phải có label và các reference không trùng.",
            )
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "references", references)


def _has_valid_shape(reference: SourceCoverageReference) -> bool:
    if reference.kind is SourceCandidateKind.COLUMN:
        return bool(reference.table_name and reference.column_name) and not (
            reference.from_column or reference.to_column
        )
    return bool(reference.from_column and reference.to_column) and not (reference.table_name or reference.column_name)


def _is_role_key(role_key: str | None) -> bool:
    if role_key is None:
        return True
    return role_key == role_key.upper() and all(character.isalnum() or character == "_" for character in role_key)
