"""Dựng explicit pending state cho clarification continuation."""

from src.application.project_sessions.clarification_answer import raise_stale_clarification
from src.application.project_sessions.conversation_context import (
    ConversationInputKind,
    PendingClarificationContext,
)
from src.application.project_sessions.conversation_context_policy import (
    ConversationMemoryInput,
)
from src.domain.project_session.clarification import ClarificationQuestionMetadata
from src.domain.project_session.entities import ProjectSession, SessionEvent


def create_clarification_memory_input(
    session: ProjectSession,
    question: SessionEvent,
    content: str,
) -> tuple[ConversationMemoryInput, str | None]:
    """Tạo input có pending snapshot trực tiếp từ question event nguồn."""
    metadata = question.metadata
    if not isinstance(metadata, ClarificationQuestionMetadata):
        raise_stale_clarification()
    pending = PendingClarificationContext(
        question.id,
        question.turn_id,
        question.content or "",
        metadata.options,
        metadata.original_intent,
        metadata.missing_information,
    )
    memory_input = ConversationMemoryInput(
        session.id,
        session.project_id,
        content,
        ConversationInputKind.CLARIFICATION_ANSWER,
        pending,
    )
    return memory_input, metadata.original_intent
