"""Codec JSONB dành riêng cho metadata clarification."""

from uuid import UUID

from src.domain.project_session.clarification import (
    ClarificationAnswerMetadata,
    ClarificationQuestionMetadata,
)
from src.domain.shared.types import JsonValue
from src.infrastructure.database.mappers.session_event.session_event_metadata_records import (
    ClarificationAnswerRecord,
    ClarificationQuestionRecord,
)


def question_to_record(
    metadata: ClarificationQuestionMetadata,
) -> ClarificationQuestionRecord:
    """Mã hóa options và reason của question."""
    return ClarificationQuestionRecord(
        options=list(metadata.options),
        allow_custom_answer=metadata.allow_custom_answer,
        reason=metadata.reason,
        original_intent=metadata.original_intent,
        missing_information=metadata.missing_information,
    )


def answer_to_record(
    metadata: ClarificationAnswerMetadata,
) -> ClarificationAnswerRecord:
    """Mã hóa liên kết answer-question."""
    return ClarificationAnswerRecord(
        question_id=str(metadata.question_id),
        kind=metadata.kind,
        option_index=metadata.option_index,
    )


def question_from_payload(
    payload: dict[str, JsonValue],
) -> ClarificationQuestionMetadata:
    """Khôi phục question metadata đã validate."""
    record = ClarificationQuestionRecord.model_validate(payload)
    return ClarificationQuestionMetadata(
        tuple(record.options),
        record.allow_custom_answer,
        record.reason,
        record.original_intent,
        record.missing_information,
    )


def answer_from_payload(
    payload: dict[str, JsonValue],
) -> ClarificationAnswerMetadata:
    """Khôi phục answer metadata đã validate."""
    record = ClarificationAnswerRecord.model_validate(payload)
    return ClarificationAnswerMetadata(UUID(record.question_id), record.kind, record.option_index)
