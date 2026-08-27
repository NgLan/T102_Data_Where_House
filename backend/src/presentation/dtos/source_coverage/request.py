"""HTTP request contracts cho Source Coverage resolution và recheck."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator
from src.application.data_warehouse_workflows.input import (
    RecheckSourceCoverageInput,
    ResolveSourceCoverageInput,
)
from src.domain.analytical_requirement.enums import SourceCoverageResolutionAction


class ResolveSourceCoverageRequest(BaseModel):
    """Structured resolution của đúng một confirmation item."""

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

    def to_application(self, project_id: UUID, assessment_id: UUID) -> ResolveSourceCoverageInput:
        """Map HTTP payload sang application input độc lập transport."""
        return ResolveSourceCoverageInput(
            project_id,
            assessment_id,
            self.batch_id,
            self.expected_source_revision,
            self.expected_resolution_revision,
            self.action,
            self.candidate_id,
        )


class RecheckSourceCoverageRequest(BaseModel):
    """Yêu cầu materialize một batch hoàn chỉnh và đánh giá lại."""

    model_config = ConfigDict(extra="forbid")
    batch_id: UUID
    expected_source_revision: int = Field(ge=0)

    def to_application(self, project_id: UUID) -> RecheckSourceCoverageInput:
        """Map HTTP payload sang application input độc lập transport."""
        return RecheckSourceCoverageInput(project_id, self.batch_id, self.expected_source_revision)
