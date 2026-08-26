"""Codec JSONB dành riêng cho metadata kết quả Agent."""

from uuid import UUID

from src.domain.project_session.value_objects import AgentResultMetadata, LLMCallStats
from src.domain.shared.types import JsonValue
from src.infrastructure.database.mappers.session_event.session_event_metadata_records import (
    AgentResultRecord,
    LlmRecord,
)


def agent_result_to_record(metadata: AgentResultMetadata) -> AgentResultRecord:
    """Mã hóa metadata kết quả Agent."""
    llm = LlmRecord.model_validate(vars(metadata.llm)) if metadata.llm else None
    return AgentResultRecord(
        session_event_id=str(metadata.session_event_id),
        agent=metadata.agent,
        status=metadata.status,
        output=metadata.output_data,
        error=metadata.error,
        llm=llm,
    )


def agent_result_from_payload(
    payload: dict[str, JsonValue],
) -> AgentResultMetadata:
    """Khôi phục metadata kết quả Agent đã validate."""
    record = AgentResultRecord.model_validate(payload)
    llm = LLMCallStats(**record.llm.model_dump()) if record.llm else None
    return AgentResultMetadata(
        record.agent,
        record.status,
        UUID(record.session_event_id),
        record.output,
        record.error,
        llm,
    )
