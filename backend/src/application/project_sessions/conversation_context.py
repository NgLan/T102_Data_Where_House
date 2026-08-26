"""Typed conversational memory built from persisted session events."""

from dataclasses import dataclass
from enum import StrEnum

from src.domain.project_session.conversation_summary import ConversationSummary
from src.domain.project_session.entities import SessionEvent
from src.domain.project_session.enums import SessionEventRole, SessionEventType
from src.domain.shared.types import EntityID

_USER_EVENTS = frozenset(
    {
        (SessionEventRole.USER, SessionEventType.MESSAGE),
        (SessionEventRole.USER, SessionEventType.ANSWER),
    }
)
_AGENT_EVENTS = frozenset(
    {
        (SessionEventRole.AGENT, SessionEventType.MESSAGE),
        (SessionEventRole.AGENT, SessionEventType.QUESTION),
    }
)


class ConversationInputKind(StrEnum):
    """Phân biệt normal message và answer của active clarification."""

    USER_MESSAGE = "USER_MESSAGE"
    CLARIFICATION_ANSWER = "CLARIFICATION_ANSWER"


@dataclass(frozen=True, slots=True)
class ConversationTurn:
    """Một User interaction và Agent response kế tiếp theo event ordering."""

    user_event_id: EntityID
    user_content: str
    agent_event_id: EntityID
    agent_content: str


@dataclass(frozen=True, slots=True)
class PendingClarificationContext:
    """Explicit workflow state inject vào clarification continuation."""

    question_id: EntityID
    turn_id: EntityID
    question: str
    options: tuple[str, ...]
    original_intent: str | None
    missing_information: str | None


@dataclass(frozen=True, slots=True)
class ConversationMemory:
    """Bounded LLM memory không thay thế persistent audit history."""

    summary: ConversationSummary | None
    recent_turns: tuple[ConversationTurn, ...]
    current_input: str
    input_kind: ConversationInputKind
    pending: PendingClarificationContext | None = None


def group_conversation_turns(events: list[SessionEvent]) -> tuple[ConversationTurn, ...]:
    """Group only public conversational events; technical events never enter memory."""
    turns: list[ConversationTurn] = []
    pending_user: SessionEvent | None = None
    for event in events:
        event_key = (event.role, event.type)
        if event_key in _USER_EVENTS:
            pending_user = event
        elif event_key in _AGENT_EVENTS and pending_user is not None:
            turns.append(_turn(pending_user, event))
            pending_user = None
    return tuple(turns)


def _turn(user: SessionEvent, agent: SessionEvent) -> ConversationTurn:
    return ConversationTurn(
        user.id,
        user.content or "",
        agent.id,
        agent.content or "",
    )
