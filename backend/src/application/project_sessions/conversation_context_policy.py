"""Policy và input models cho bounded conversation context."""

from dataclasses import dataclass

from src.application.project_sessions.conversation_context import (
    ConversationInputKind,
    PendingClarificationContext,
)
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class ConversationContextPolicy:
    """Engineering defaults có thể cấu hình cho raw turns và summary batch."""

    recent_turns: int = 6
    summary_batch_size: int = 4


@dataclass(frozen=True, slots=True)
class ConversationMemoryInput:
    """Current workflow state dùng để dựng context cho một invocation."""

    session_id: EntityID
    project_id: EntityID
    current_input: str
    input_kind: ConversationInputKind
    pending: PendingClarificationContext | None = None
