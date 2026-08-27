"""Semantic metadata được người dùng xác nhận cho nguồn dữ liệu."""

from dataclasses import dataclass

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_source.enums import (
    SourceSemanticDecision,
    SourceSemanticProvenance,
)
from src.domain.shared.enum_rules import normalize_str_enum
from src.domain.shared.types import EntityID
from src.domain.shared.value_object import BaseValueObject


@dataclass(frozen=True)
class SourceSemanticAnnotation(BaseValueObject):
    """Một kết luận nghiệp vụ có provenance rõ ràng trên source hiện hữu."""

    requirement_id: EntityID | None
    required_concept_key: str
    decision: SourceSemanticDecision
    provenance: SourceSemanticProvenance = SourceSemanticProvenance.USER
    candidate_label: str | None = None
    role_key: str | None = None
    role_label: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "required_concept_key", _concept_key(self.required_concept_key))
        object.__setattr__(
            self,
            "decision",
            normalize_str_enum(self.decision, SourceSemanticDecision, ErrorCode.VALIDATION_ERROR),
        )
        object.__setattr__(
            self,
            "provenance",
            normalize_str_enum(self.provenance, SourceSemanticProvenance, ErrorCode.VALIDATION_ERROR),
        )
        candidate_label, role_key, role_label = _normalized_labels(self)
        object.__setattr__(self, "candidate_label", candidate_label)
        object.__setattr__(self, "role_key", role_key)
        object.__setattr__(self, "role_label", role_label)


def _concept_key(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise BusinessException(
            ErrorCode.VALIDATION_ERROR,
            "Khái niệm nghiệp vụ của source không được để trống.",
        )
    return normalized


def _normalized_labels(
    annotation: SourceSemanticAnnotation,
) -> tuple[str | None, str | None, str | None]:
    candidate = annotation.candidate_label.strip() if annotation.candidate_label else None
    role_key = annotation.role_key.strip() if annotation.role_key else None
    role_label = annotation.role_label.strip() if annotation.role_label else None
    if bool(role_key) != bool(role_label):
        raise BusinessException(
            ErrorCode.VALIDATION_ERROR,
            "Role của source semantic annotation không hợp lệ.",
        )
    return candidate, role_key, role_label


def merge_semantic_annotation(
    current: tuple[SourceSemanticAnnotation, ...],
    annotation: SourceSemanticAnnotation,
) -> tuple[SourceSemanticAnnotation, ...]:
    """Thay quyết định cũ cho cùng concept/provenance bằng quyết định mới."""
    retained = tuple(
        item
        for item in current
        if not (
            item.requirement_id == annotation.requirement_id
            and item.required_concept_key.casefold() == annotation.required_concept_key.casefold()
            and item.provenance is annotation.provenance
        )
    )
    return (*retained, annotation)


def remove_semantic_annotation(
    current: tuple[SourceSemanticAnnotation, ...],
    requirement_id: EntityID,
    concept_key: str,
) -> tuple[SourceSemanticAnnotation, ...]:
    """Xóa USER decision thuộc đúng Requirement và concept key."""
    return tuple(
        item
        for item in current
        if not (
            item.requirement_id == requirement_id
            and item.required_concept_key.casefold() == concept_key.casefold()
            and item.provenance is SourceSemanticProvenance.USER
        )
    )
