"""Immutable inputs cho session event factory."""

from dataclasses import dataclass

from src.domain.project_session.entities import SessionEvent
from src.domain.project_session.enums import (
    AgentResultStatus,
    AgentType,
    ClarificationAnswerKind,
)
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class UserEventInput:
    """Input tạo public User message."""

    session_id: EntityID
    turn_id: EntityID
    content: str


@dataclass(frozen=True, slots=True)
class AgentCallEventInput:
    """Input tạo technical Agent call với operation cụ thể."""

    session_id: EntityID
    turn_id: EntityID
    target_agent: AgentType
    operation: str


@dataclass(frozen=True, slots=True)
class AgentResultEventInput:
    """Input tạo technical Agent result audit event."""

    call: SessionEvent
    status: AgentResultStatus
    content: str
    output: str | None = None


@dataclass(frozen=True, slots=True)
class AgentMessageEventInput:
    """Input tạo public Agent message liên kết technical result."""

    result: SessionEvent
    content: str
    proposal_change_id: EntityID | None = None


@dataclass(frozen=True, slots=True)
class QuestionEventInput:
    """Input tạo public clarification question."""

    session_id: EntityID
    turn_id: EntityID
    question: str
    options: tuple[str, ...]
    allow_custom_answer: bool
    reason: str | None = None
    original_intent: str | None = None
    missing_information: str | None = None


@dataclass(frozen=True, slots=True)
class AnswerEventInput:
    """Input tạo User answer liên kết pending question."""

    session_id: EntityID
    turn_id: EntityID
    question_id: EntityID
    content: str
    kind: ClarificationAnswerKind
    option_index: int | None = None
