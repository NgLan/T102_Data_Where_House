"""HTTP contracts for Source Coverage batches and structured resolutions."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator
from src.application.data_warehouse_workflows.input import (
    RecheckSourceCoverageInput,
    ResolveSourceCoverageInput,
)
from src.domain.analytical_requirement.enums import (
    SourceCandidateKind,
    SourceConfirmationStatus,
    SourceCoverageResolutionAction,
    SourceCoverageStatus,
)


class SourceCoverageCandidateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    kind: SourceCandidateKind
    source_id: UUID
    source_name: str
    table_name: str | None = None
    column_name: str | None = None
    from_column: str | None = None
    to_column: str | None = None


class SourceCoverageAssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    analytical_requirement_id: UUID
    requirement_id: UUID
    requirement_title: str
    coverage_status: SourceCoverageStatus
    required_concept_key: str
    title: str
    explanation: str
    question: str | None = None
    confirmation_status: SourceConfirmationStatus | None = None
    selected_candidate_id: UUID | None = None
    resolution_revision: int = Field(ge=0)
    candidates: list[SourceCoverageCandidateResponse]


class SourceCoverageBatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    evaluated_source_revision: int = Field(ge=0)
    confirmation_total: int = Field(ge=0)
    confirmation_resolved: int = Field(ge=0)
    can_recheck: bool
    assessments: list[SourceCoverageAssessmentResponse]


class ResolveSourceCoverageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    batch_id: UUID
    expected_source_revision: int = Field(ge=0)
    expected_resolution_revision: int = Field(ge=0)
    action: SourceCoverageResolutionAction
    candidate_id: UUID | None = None

    @model_validator(mode="after")
    def validate_candidate(self) -> "ResolveSourceCoverageRequest":
        needs_id = self.action is SourceCoverageResolutionAction.CONFIRM_CANDIDATE
        if needs_id != (self.candidate_id is not None):
            raise ValueError("candidate_id chỉ được yêu cầu khi CONFIRM_CANDIDATE.")
        return self

    def to_application(
        self, project_id: UUID, assessment_id: UUID
    ) -> ResolveSourceCoverageInput:
        return ResolveSourceCoverageInput(
            project_id, assessment_id, self.batch_id,
            self.expected_source_revision, self.expected_resolution_revision,
            self.action, self.candidate_id,
        )


class RecheckSourceCoverageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    batch_id: UUID
    expected_source_revision: int = Field(ge=0)

    def to_application(self, project_id: UUID) -> RecheckSourceCoverageInput:
        return RecheckSourceCoverageInput(
            project_id, self.batch_id, self.expected_source_revision
        )
