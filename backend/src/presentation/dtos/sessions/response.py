"""Response DTO công khai cho phiên và event Agent."""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from src.application.project_sessions.output import ProjectSessionOutput, SessionEventOutput, SessionTurnOutput
from src.domain.project_session.enums import AgentResultStatus, SessionEventRole, SessionEventType, SessionStatus


class ProjectSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    title: str
    status: SessionStatus
    is_running: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_application(cls, output: ProjectSessionOutput) -> "ProjectSessionResponse":
        return cls.model_validate(output)


class SessionEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_id: UUID
    turn_id: UUID | None
    role: SessionEventRole
    type: SessionEventType
    content: str | None
    status: AgentResultStatus | None
    proposal_change_id: UUID | None
    created_at: datetime

    @classmethod
    def from_application(cls, output: SessionEventOutput) -> "SessionEventResponse":
        return cls.model_validate(output)


class ClarificationTurnResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: UUID
    turn_id: UUID
    kind: Literal["clarification"]
    question: str
    summary: str | None = None


class ProposalTurnResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: UUID
    turn_id: UUID
    kind: Literal["proposal"]
    proposal_change_id: UUID
    summary: str | None = None


AgentTurnResponse = Annotated[
    ClarificationTurnResponse | ProposalTurnResponse,
    Field(discriminator="kind"),
]


def create_agent_turn_response(output: SessionTurnOutput) -> AgentTurnResponse:
    if output.kind == "clarification" and output.question:
        return ClarificationTurnResponse.model_validate(output)
    if output.kind == "proposal" and output.proposal_change_id:
        return ProposalTurnResponse.model_validate(output)
    raise ValueError("Agent turn result is incomplete.")
