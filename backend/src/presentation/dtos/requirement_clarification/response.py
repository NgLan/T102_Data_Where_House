"""Response payload cho Requirement clarification workspace."""

from pydantic import BaseModel, Field
from src.application.requirements.output import RequirementClarificationStateOutput
from src.domain.project_session.enums import (
    RequirementClarificationStatus,
    RequirementContinuationState,
)
from src.presentation.dtos.requirements.response import RequirementResponse
from src.presentation.dtos.sessions.response import (
    ClarificationQuestionResponse,
    ProjectSessionResponse,
)


class RequirementClarificationResponse(BaseModel):
    """Canonical structured state và derived UI status của current cycle."""

    session: ProjectSessionResponse | None
    status: RequirementClarificationStatus
    pending_question: ClarificationQuestionResponse | None
    requirements: list[RequirementResponse]
    requirement_revision: int = Field(ge=0)
    analyzed_requirement_revision: int = Field(ge=0)
    is_outdated: bool
    continuation_state: RequirementContinuationState

    @classmethod
    def from_application(
        cls, output: RequirementClarificationStateOutput
    ) -> "RequirementClarificationResponse":
        """Ánh xạ application state sang public payload."""
        return cls(
            session=(
                ProjectSessionResponse.from_application(output.session)
                if output.session
                else None
            ),
            status=output.status,
            pending_question=(
                ClarificationQuestionResponse.from_application(output.pending_question)
                if output.pending_question
                else None
            ),
            requirements=[
                RequirementResponse.from_application(item) for item in output.requirements
            ],
            requirement_revision=output.requirement_revision,
            analyzed_requirement_revision=output.analyzed_requirement_revision,
            is_outdated=output.is_outdated,
            continuation_state=output.continuation_state,
        )
