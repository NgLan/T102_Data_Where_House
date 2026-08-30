"""Codec JSONB cho metadata của SessionEvent."""

from uuid import UUID

from pydantic import ValidationError
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.project_session.clarification import ClarificationAnswerMetadata, ClarificationQuestionMetadata
from src.domain.project_session.value_objects import (
    AgentCallMetadata,
    AgentResultMetadata,
    MessageMetadata,
    SessionEventMetadata,
    ToolCallMetadata,
    ToolResultMetadata,
)
from src.domain.shared.types import JsonValue
from src.infrastructure.database.mappers.session_event.agent_result_metadata_codec import (
    agent_result_from_payload,
    agent_result_to_record,
)
from src.infrastructure.database.mappers.session_event.clarification_metadata_codec import (
    answer_from_payload,
    answer_to_record,
    question_from_payload,
    question_to_record,
)
from src.infrastructure.database.mappers.session_event.session_event_metadata_records import (
    AgentCallRecord,
    MessageRecord,
    MetadataRecord,
    ToolCallRecord,
    ToolResultRecord,
)


def encode_event_metadata(metadata: SessionEventMetadata | None) -> dict[str, JsonValue] | None:
    """Chuyển metadata Domain thành payload JSONB."""
    if metadata is None:
        return None
    record = _to_record(metadata)
    return record.model_dump(mode="json")


def decode_event_metadata(
    payload: dict[str, JsonValue] | None,
    metadata_type: type[SessionEventMetadata] | None,
) -> SessionEventMetadata | None:
    """Khôi phục metadata theo contract của event type."""
    if payload is None or metadata_type is None:
        return None
    try:
        return _from_payload(payload, metadata_type)
    except (ValidationError, ValueError) as exc:
        raise InfrastructureException(
            code=ErrorCode.DATABASE_ERROR,
            message="Metadata sự kiện phiên trong cơ sở dữ liệu không hợp lệ.",
        ) from exc


def _to_record(metadata: SessionEventMetadata) -> MetadataRecord:
    if isinstance(metadata, MessageMetadata):
        return MessageRecord(
            model=metadata.model,
            agent_result_id=str(metadata.agent_result_id) if metadata.agent_result_id else None,
            proposal_change_id=(str(metadata.proposal_change_id) if metadata.proposal_change_id else None),
            client_message_id=(str(metadata.client_message_id) if metadata.client_message_id else None),
        )
    if isinstance(metadata, ClarificationQuestionMetadata):
        return question_to_record(metadata)
    if isinstance(metadata, ClarificationAnswerMetadata):
        return answer_to_record(metadata)
    if isinstance(metadata, AgentCallMetadata):
        return AgentCallRecord(
            caller_agent=metadata.caller_agent,
            target_agent=metadata.target_agent,
            input=metadata.input_data,
        )
    if isinstance(metadata, AgentResultMetadata):
        return agent_result_to_record(metadata)
    if isinstance(metadata, ToolCallMetadata):
        return ToolCallRecord(agent=metadata.agent, tool=metadata.tool, arguments=metadata.arguments)
    if isinstance(metadata, ToolResultMetadata):
        return _tool_result_record(metadata)
    raise ValueError("Unsupported session event metadata type.")


def _tool_result_record(metadata: ToolResultMetadata) -> ToolResultRecord:
    """Mã hóa metadata kết quả tool."""
    return ToolResultRecord(
        session_event_id=str(metadata.session_event_id),
        tool=metadata.tool,
        status=metadata.status,
        result=metadata.result_data,
        error=metadata.error,
    )


def _from_payload(
    payload: dict[str, JsonValue],
    metadata_type: type[SessionEventMetadata],
) -> SessionEventMetadata:
    if metadata_type is MessageMetadata:
        return _message_from_payload(payload)
    if metadata_type is ClarificationQuestionMetadata:
        return question_from_payload(payload)
    if metadata_type is ClarificationAnswerMetadata:
        return answer_from_payload(payload)
    if metadata_type is AgentCallMetadata:
        record = AgentCallRecord.model_validate(payload)
        return AgentCallMetadata(record.caller_agent, record.target_agent, record.input)
    if metadata_type is AgentResultMetadata:
        return agent_result_from_payload(payload)
    if metadata_type is ToolCallMetadata:
        record = ToolCallRecord.model_validate(payload)
        return ToolCallMetadata(record.agent, record.tool, record.arguments)
    if metadata_type is ToolResultMetadata:
        record = ToolResultRecord.model_validate(payload)
        return ToolResultMetadata(
            record.tool, record.status, UUID(record.session_event_id), record.result, record.error
        )
    raise ValueError("Unsupported session event metadata type.")


def _message_from_payload(payload: dict[str, JsonValue]) -> MessageMetadata:
    record = MessageRecord.model_validate(payload)
    return MessageMetadata(
        record.model,
        UUID(record.agent_result_id) if record.agent_result_id else None,
        UUID(record.proposal_change_id) if record.proposal_change_id else None,
        UUID(record.client_message_id) if record.client_message_id else None,
    )
