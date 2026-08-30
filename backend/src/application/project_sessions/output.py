"""Output models an toàn cho API phiên Agent."""

from dataclasses import dataclass
from datetime import datetime

from src.application.data_warehouse_workflows.output import AgentTurnKind
from src.application.project_sessions.session_event_output import (
    SessionEventOutput as SessionEventOutput,
)
from src.domain.project_session.entities import ProjectSession
from src.domain.project_session.enums import (
    SessionPurpose,
    SessionQuestionKind,
    SessionStatus,
    ToolResultStatus,
)
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class ProjectSessionOutput:
    id: EntityID
    project_id: EntityID
    title: str
    status: SessionStatus
    purpose: SessionPurpose
    base_requirement_revision: int | None
    is_running: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, session: ProjectSession) -> "ProjectSessionOutput":
        """Làm phẳng session, không lộ user nội bộ."""
        return cls(
            session.id,
            session.project_id,
            session.title,
            session.status,
            session.purpose,
            session.base_requirement_revision,
            session.active_turn_id is not None,
            session.created_at,
            session.updated_at,
        )


@dataclass(frozen=True, slots=True)
class SessionTurnOutput:
    session_id: EntityID
    turn_id: EntityID
    kind: AgentTurnKind
    question_id: EntityID | None = None
    question: str | None = None
    options: tuple[str, ...] = ()
    allow_custom_answer: bool = False
    reason: str | None = None
    proposal_change_id: EntityID | None = None
    summary: str | None = None
    question_kind: SessionQuestionKind | None = None
    tool_name: str | None = None
    tool_status: ToolResultStatus | None = None
    artifact_event_id: EntityID | None = None


@dataclass(frozen=True, slots=True)
class ToolArtifactDownloadOutput:
    filename: str
    mime_type: str
    content: bytes
