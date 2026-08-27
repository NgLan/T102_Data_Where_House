"""HTTP response contracts cho typed Source Coverage batches."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from src.domain.analytical_requirement.enums import (
    SourceCandidateKind,
    SourceConfirmationQuestionType,
    SourceConfirmationStatus,
    SourceCoverageStatus,
)


class SourceCoverageReferenceResponse(BaseModel):
    """Exact source evidence thuộc một candidate mapping."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")
    kind: SourceCandidateKind
    source_id: UUID
    source_name: str
    role_key: str | None = None
    role_label: str | None = None
    table_name: str | None = None
    column_name: str | None = None
    from_column: str | None = None
    to_column: str | None = None


class SourceCoverageCandidateResponse(BaseModel):
    """Một selectable business mapping và toàn bộ evidence của nó."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")
    id: UUID
    label: str
    references: list[SourceCoverageReferenceResponse]


class SourceCoverageAssessmentResponse(BaseModel):
    """Coverage assessment cùng typed question contract nếu cần xác nhận."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")
    id: UUID
    analytical_requirement_id: UUID
    requirement_id: UUID
    requirement_title: str
    coverage_status: SourceCoverageStatus
    required_concept_key: str
    title: str
    explanation: str
    question: str | None = None
    question_type: SourceConfirmationQuestionType | None = None
    confirmation_status: SourceConfirmationStatus | None = None
    selected_candidate_id: UUID | None = None
    resolution_revision: int = Field(ge=0)
    candidates: list[SourceCoverageCandidateResponse]


class SourceCoverageBatchResponse(BaseModel):
    """Stable Source Confirmation batch của project revision hiện hành."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")
    id: UUID
    evaluated_source_revision: int = Field(ge=0)
    confirmation_total: int = Field(ge=0)
    confirmation_resolved: int = Field(ge=0)
    can_recheck: bool
    assessments: list[SourceCoverageAssessmentResponse]
