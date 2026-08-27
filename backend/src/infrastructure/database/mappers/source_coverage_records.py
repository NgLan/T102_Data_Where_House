"""Persistence records cho source coverage JSONB."""

from uuid import UUID

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator
from src.domain.analytical_requirement.enums import (
    SourceCandidateKind,
    SourceConfirmationQuestionType,
    SourceConfirmationStatus,
    SourceCoverageStatus,
)


class SourceCoverageReferenceRecord(BaseModel):
    """Typed source reference nằm trong một candidate mapping."""

    model_config = ConfigDict(extra="forbid")
    kind: SourceCandidateKind
    source_id: UUID
    role_key: str | None = None
    role_label: str | None = None
    table_name: str | None = None
    column_name: str | None = None
    from_column: str | None = None
    to_column: str | None = None


class SourceCoverageCandidateRecord(BaseModel):
    """Typed candidate mapping lưu cùng Analytical Requirement."""

    model_config = ConfigDict(extra="forbid")
    id: UUID
    label: str
    references: list[SourceCoverageReferenceRecord] = Field(min_length=1)


class SourceCoverageAssessmentRecord(BaseModel):
    """Typed assessment record với invariant theo coverage status."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    id: UUID
    batch_id: UUID | None = None
    evaluated_source_revision: int = Field(default=0, ge=0)
    status: SourceCoverageStatus
    required_concept_key: str = Field(validation_alias=AliasChoices("required_concept_key", "required_concept"))
    title: str = Field(validation_alias=AliasChoices("title", "required_concept"))
    explanation: str = Field(validation_alias=AliasChoices("explanation", "reason"))
    question: str | None = None
    question_type: SourceConfirmationQuestionType | None = None
    confirmation_status: SourceConfirmationStatus | None = None
    selected_candidate_id: UUID | None = None
    resolution_revision: int = Field(default=0, ge=0)
    applied_source_revision: int | None = Field(default=None, ge=0)
    candidates: list[SourceCoverageCandidateRecord] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def upgrade_legacy_candidates(cls, value: object) -> object:
        """Bọc atomic candidates cũ để batch vẫn đọc được trước reanalysis."""
        if not isinstance(value, dict):
            return value
        candidates = value.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            return value
        if not isinstance(candidates[0], dict) or "references" in candidates[0]:
            return value
        return _upgrade_legacy_assessment(value, candidates)

    @model_validator(mode="after")
    def validate_candidates(self) -> "SourceCoverageAssessmentRecord":
        needs_confirmation = self.status is SourceCoverageStatus.NEEDS_SOURCE_CONFIRMATION
        if needs_confirmation != bool(self.candidates and self.question_type):
            raise ValueError("Source confirmation shape is invalid.")
        if not needs_confirmation and (self.question or self.question_type or self.candidates):
            raise ValueError("Only source confirmation can contain question data.")
        if needs_confirmation:
            self.confirmation_status = self.confirmation_status or SourceConfirmationStatus.PENDING
        return self


def _upgrade_legacy_assessment(value: dict[object, object], candidates: list[object]) -> dict[object, object]:
    upgraded = dict(value)
    atomic = [dict(item) for item in candidates if isinstance(item, dict)]
    relationships = [item for item in atomic if item.get("kind") == "RELATIONSHIP"]
    if relationships:
        upgraded["question_type"] = "RELATIONSHIP_CONFIRMATION"
        upgraded["candidates"] = [_legacy_relationship_mapping(relationships)]
        if upgraded.get("confirmation_status") == "CONFIRMED":
            upgraded["selected_candidate_id"] = relationships[0]["id"]
    else:
        upgraded["question_type"] = "SINGLE_CANDIDATE_CONFIRMATION" if len(atomic) == 1 else "SINGLE_FIELD_SELECTION"
        upgraded["candidates"] = [_legacy_column_mapping(item) for item in atomic]
    return upgraded


def _legacy_column_mapping(item: dict[object, object]) -> dict[str, object]:
    reference = {key: value for key, value in item.items() if key != "id"}
    return {
        "id": item["id"],
        "label": str(item.get("column_name") or "Source field"),
        "references": [reference],
    }


def _legacy_relationship_mapping(items: list[dict[object, object]]) -> dict[str, object]:
    references = [{key: value for key, value in item.items() if key != "id"} for item in items]
    first = items[0]
    return {
        "id": first["id"],
        "label": f"{first.get('from_column')} → {first.get('to_column')}",
        "references": references,
    }
