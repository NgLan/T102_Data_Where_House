"""Structured long-term conversational state for an Agent session."""

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.shared.types import EntityID
from src.domain.shared.value_object import BaseValueObject

if TYPE_CHECKING:
    from src.domain.project_session.entities import ProjectSession


@dataclass(frozen=True)
class SummaryItem(BaseValueObject):
    """Một conversational fact có event evidence, không sao chép canonical state."""

    statement: str
    evidence_event_ids: tuple[EntityID, ...] = ()

    def __post_init__(self) -> None:
        statement = self.statement.strip()
        if not statement:
            _raise_invalid("Conversation summary item không được để trống.")
        if not self.evidence_event_ids:
            _raise_invalid("Conversation summary item phải có evidence event ID.")
        object.__setattr__(self, "statement", statement)


@dataclass(frozen=True)
class SummaryDecision(BaseValueObject):
    """Quyết định active duy nhất theo một semantic key."""

    key: str
    value: str
    evidence_event_ids: tuple[EntityID, ...] = ()

    def __post_init__(self) -> None:
        key, value = self.key.strip(), self.value.strip()
        if not key or not value:
            _raise_invalid("Conversation decision phải có key và value.")
        if not self.evidence_event_ids:
            _raise_invalid("Conversation decision phải có evidence event ID.")
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "value", value)


@dataclass(frozen=True)
class ResolvedClarification(BaseValueObject):
    """Business meaning đã được xác nhận qua một cặp question-answer."""

    question: str
    answer: str
    question_event_id: EntityID
    answer_event_id: EntityID

    def __post_init__(self) -> None:
        question, answer = self.question.strip(), self.answer.strip()
        if not question or not answer:
            _raise_invalid("Resolved clarification phải có question và answer.")
        object.__setattr__(self, "question", question)
        object.__setattr__(self, "answer", answer)


@dataclass(frozen=True)
class ConversationSummary(BaseValueObject):
    """Current conversational state; canonical project data chỉ được tham chiếu."""

    current_goal: SummaryItem | None = None
    confirmed_decisions: tuple[SummaryDecision, ...] = ()
    resolved_clarifications: tuple[ResolvedClarification, ...] = ()
    important_constraints: tuple[SummaryItem, ...] = ()
    current_task: SummaryItem | None = None
    open_questions: tuple[SummaryItem, ...] = ()
    rejected_assumptions: tuple[SummaryItem, ...] = ()
    canonical_references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        keys = tuple(item.key.casefold() for item in self.confirmed_decisions)
        if len(keys) != len(set(keys)):
            _raise_invalid("Conversation summary không được có duplicate decision key.")
        references = tuple(item.strip() for item in self.canonical_references if item.strip())
        object.__setattr__(self, "canonical_references", tuple(dict.fromkeys(references)))


@dataclass(frozen=True)
class ConversationSummaryUpdate(BaseValueObject):
    """Atomic summary checkpoint update applied under a session row lock."""

    summary: ConversationSummary
    through_event_id: EntityID
    updated_at: datetime


def apply_summary_update(
    session: "ProjectSession", update: ConversationSummaryUpdate
) -> None:
    """Advance summary checkpoint idempotently dưới session row lock."""
    if session.summarized_through_event_id == update.through_event_id:
        return
    session.conversation_summary = update.summary
    session.summarized_through_event_id = update.through_event_id
    session.summary_updated_at = update.updated_at
    session.mark_updated()


def _raise_invalid(message: str) -> None:
    raise BusinessException(ErrorCode.VALIDATION_ERROR, message)
