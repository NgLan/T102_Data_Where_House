"""JSONB codec for the ProjectSession structured conversation summary."""

from uuid import UUID

from src.domain.project_session.conversation_summary import (
    ConversationSummary,
    ResolvedClarification,
    SummaryDecision,
    SummaryItem,
)
from src.domain.shared.types import JsonValue
from src.infrastructure.database.mappers.conversation_summary_record import (
    ConversationSummaryRecord,
    ResolvedClarificationRecord,
    SummaryDecisionRecord,
    SummaryItemRecord,
)


def encode_conversation_summary(
    summary: ConversationSummary | None,
) -> dict[str, JsonValue] | None:
    """Serialize a domain summary into validated JSONB primitives."""
    if summary is None:
        return None
    record = ConversationSummaryRecord(
        current_goal=_item_record(summary.current_goal),
        confirmed_decisions=[_decision_record(item) for item in summary.confirmed_decisions],
        resolved_clarifications=[
            ResolvedClarificationRecord(
                question=item.question,
                answer=item.answer,
                question_event_id=str(item.question_event_id),
                answer_event_id=str(item.answer_event_id),
            )
            for item in summary.resolved_clarifications
        ],
        important_constraints=[_item_record(item) for item in summary.important_constraints],
        current_task=_item_record(summary.current_task),
        open_questions=[_item_record(item) for item in summary.open_questions],
        rejected_assumptions=[_item_record(item) for item in summary.rejected_assumptions],
        canonical_references=list(summary.canonical_references),
    )
    return record.model_dump(mode="json")


def decode_conversation_summary(
    payload: dict[str, JsonValue] | None,
) -> ConversationSummary | None:
    """Restore a validated domain summary from JSONB."""
    if payload is None:
        return None
    record = ConversationSummaryRecord.model_validate(payload)
    return ConversationSummary(
        current_goal=_item(record.current_goal),
        confirmed_decisions=tuple(_decision(item) for item in record.confirmed_decisions),
        resolved_clarifications=tuple(
            ResolvedClarification(
                item.question,
                item.answer,
                UUID(item.question_event_id),
                UUID(item.answer_event_id),
            )
            for item in record.resolved_clarifications
        ),
        important_constraints=tuple(_item(item) for item in record.important_constraints),
        current_task=_item(record.current_task),
        open_questions=tuple(_item(item) for item in record.open_questions),
        rejected_assumptions=tuple(_item(item) for item in record.rejected_assumptions),
        canonical_references=tuple(record.canonical_references),
    )


def _item_record(item: SummaryItem | None) -> SummaryItemRecord | None:
    if item is None:
        return None
    return SummaryItemRecord(
        statement=item.statement,
        evidence_event_ids=[str(event_id) for event_id in item.evidence_event_ids],
    )


def _decision_record(item: SummaryDecision) -> SummaryDecisionRecord:
    return SummaryDecisionRecord(
        key=item.key,
        value=item.value,
        evidence_event_ids=[str(event_id) for event_id in item.evidence_event_ids],
    )


def _item(item: SummaryItemRecord | None) -> SummaryItem | None:
    if item is None:
        return None
    return SummaryItem(item.statement, tuple(UUID(event_id) for event_id in item.evidence_event_ids))


def _decision(item: SummaryDecisionRecord) -> SummaryDecision:
    return SummaryDecision(
        item.key,
        item.value,
        tuple(UUID(event_id) for event_id in item.evidence_event_ids),
    )
