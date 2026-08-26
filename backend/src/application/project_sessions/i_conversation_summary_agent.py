"""Outbound port cho Agent compact conversation summary."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.application.project_sessions.conversation_context import ConversationTurn
from src.domain.project_session.conversation_summary import ConversationSummary


@dataclass(frozen=True, slots=True)
class ConversationSummaryInput:
    """Snapshot đầy đủ cần thiết cho một lần cumulative compaction."""

    previous_summary: ConversationSummary | None
    turns: tuple[ConversationTurn, ...]
    canonical_context_index: tuple[str, ...]


class IConversationSummaryAgent(ABC):
    """Tạo structured summary mà không sao chép canonical project state."""

    @abstractmethod
    async def summarize(self, data: ConversationSummaryInput) -> ConversationSummary:
        """Trả toàn bộ current summary sau khi hợp nhất batch mới."""
