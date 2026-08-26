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

    def __post_init__(self) -> None:
        concept_key = self.required_concept_key.strip()
        if not concept_key:
            raise BusinessException(
                ErrorCode.VALIDATION_ERROR,
                "Khái niệm nghiệp vụ của source không được để trống.",
            )
        object.__setattr__(self, "required_concept_key", concept_key)
        object.__setattr__(
            self,
            "decision",
            normalize_str_enum(
                self.decision,
                SourceSemanticDecision,
                ErrorCode.VALIDATION_ERROR,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            normalize_str_enum(
                self.provenance,
                SourceSemanticProvenance,
                ErrorCode.VALIDATION_ERROR,
            ),
        )


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
            and item.required_concept_key.casefold()
            == annotation.required_concept_key.casefold()
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
