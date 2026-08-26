"""Validation helpers cho Agent-produced summary references."""

from uuid import UUID

from src.infrastructure.llm.conversation_summary_output import ConversationSummaryOutput


def validate_canonical_references(
    output: ConversationSummaryOutput, canonical_index: frozenset[str]
) -> tuple[str, ...]:
    """Chỉ chấp nhận exact reference đã có trong canonical dedup index."""
    references = tuple(output.canonical_references)
    if not set(references).issubset(canonical_index):
        raise ValueError("Summary contains a canonical reference outside the supplied index.")
    return references


def require_allowed_event_id(value: str, allowed: frozenset[UUID]) -> UUID:
    """Chỉ chấp nhận evidence từ previous summary hoặc batch đang compact."""
    event_id = UUID(value)
    if event_id not in allowed:
        raise ValueError("Summary evidence ID is outside previous summary or compacted batch.")
    return event_id
