"""Input models độc lập HTTP cho phiên Agent."""

from dataclasses import dataclass

from src.domain.project_session.enums import SessionPurpose
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class CreateSessionInput:
    project_id: EntityID
    purpose: SessionPurpose
    title: str | None = None


@dataclass(frozen=True, slots=True)
class ListSessionsInput:
    project_id: EntityID
    purpose: SessionPurpose


@dataclass(frozen=True, slots=True)
class GetSessionInput:
    session_id: EntityID


@dataclass(frozen=True, slots=True)
class RenameSessionInput:
    session_id: EntityID
    title: str


@dataclass(frozen=True, slots=True)
class ListSessionEventsInput:
    session_id: EntityID
    after_id: EntityID | None = None
    limit: int = 50
    conversation_only: bool = False


@dataclass(frozen=True, slots=True)
class SendSessionMessageInput:
    session_id: EntityID
    content: str
    client_message_id: EntityID | None = None
    locale: str = "vi"


@dataclass(frozen=True, slots=True)
class GetPendingClarificationInput:
    session_id: EntityID


@dataclass(frozen=True, slots=True)
class AnswerClarificationInput:
    session_id: EntityID
    question_id: EntityID
    option_index: int | None = None
    custom_answer: str | None = None


@dataclass(frozen=True, slots=True)
class GetToolArtifactInput:
    session_id: EntityID
    tool_result_event_id: EntityID
