"""Persistence records cho source coverage JSONB."""

from uuid import UUID

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator
from src.domain.analytical_requirement.enums import (
    SourceCandidateKind,
    SourceConfirmationStatus,
    SourceCoverageStatus,
)


class SourceCoverageCandidateRecord(BaseModel):
    """Typed candidate reference lưu cùng Analytical Requirement."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    id: UUID
    kind: SourceCandidateKind
    source_id: UUID
    table_name: str | None = None
    column_name: str | None = None
    from_column: str | None = None
    to_column: str | None = None


class SourceCoverageAssessmentRecord(BaseModel):
    """Typed assessment record với invariant theo coverage status."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    id: UUID
    batch_id: UUID | None = None
    evaluated_source_revision: int = Field(default=0, ge=0)
    status: SourceCoverageStatus
    required_concept_key: str = Field(
        validation_alias=AliasChoices("required_concept_key", "required_concept")
    )
    title: str = Field(validation_alias=AliasChoices("title", "required_concept"))
    explanation: str = Field(validation_alias=AliasChoices("explanation", "reason"))
    question: str | None = None
    confirmation_status: SourceConfirmationStatus | None = None
    selected_candidate_id: UUID | None = None
    resolution_revision: int = Field(default=0, ge=0)
    applied_source_revision: int | None = Field(default=None, ge=0)
    candidates: list[SourceCoverageCandidateRecord] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_candidates(self) -> "SourceCoverageAssessmentRecord":
        if self.status is SourceCoverageStatus.NEEDS_SOURCE_CONFIRMATION:
            if not self.candidates:
                raise ValueError("Source confirmation requires candidates.")
            self.confirmation_status = (
                self.confirmation_status or SourceConfirmationStatus.PENDING
            )
        if self.status is SourceCoverageStatus.MISSING_SOURCE and self.candidates:
            raise ValueError("Missing source cannot contain candidates.")
        return self
