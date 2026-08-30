"""Safe projection of persisted session events for application consumers."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.common.utils.json import safe_json_loads
from src.domain.project_session.clarification import (
    ClarificationAnswerMetadata,
    ClarificationQuestionMetadata,
)
from src.domain.project_session.entities import SessionEvent
from src.domain.project_session.enums import (
    AgentResultStatus,
    SessionEventRole,
    SessionEventType,
    SessionQuestionKind,
    ToolResultStatus,
)
from src.domain.project_session.value_objects import (
    AgentResultMetadata,
    MessageMetadata,
    ToolResultMetadata,
)
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class SessionEventOutput:
    id: EntityID
    session_id: EntityID
    turn_id: EntityID | None
    role: SessionEventRole
    type: SessionEventType
    content: str | None
    status: AgentResultStatus | None
    proposal_change_id: EntityID | None
    question_options: tuple[str, ...]
    allow_custom_answer: bool
    answer_to_question_id: EntityID | None
    client_message_id: EntityID | None
    question_kind: SessionQuestionKind | None
    tool_name: str | None
    tool_status: ToolResultStatus | None
    artifact_id: EntityID | None
    artifact_filename: str | None
    artifact_mime_type: str | None
    sandbox_schema_name: str | None
    sandbox_endpoint_risk: str | None
    executed_statements: int | None
    succeeded_statements: int | None
    failed_statements: int | None
    total_duration_ms: float | None
    created_at: datetime

    @classmethod
    def from_domain(cls, event: SessionEvent) -> "SessionEventOutput":
        return cls(*_base_values(event), *_metadata_values(event), event.created_at)


def _question(event: SessionEvent) -> ClarificationQuestionMetadata | None:
    return event.metadata if isinstance(event.metadata, ClarificationQuestionMetadata) else None


def _base_values(event: SessionEvent) -> tuple[object, ...]:
    return (
        event.id,
        event.session_id,
        event.turn_id,
        event.role,
        event.type,
        event.content,
    )


def _metadata_values(event: SessionEvent) -> tuple[object, ...]:
    question = _question(event)
    answer = event.metadata if isinstance(event.metadata, ClarificationAnswerMetadata) else None
    message = event.metadata if isinstance(event.metadata, MessageMetadata) else None
    tool = event.metadata if isinstance(event.metadata, ToolResultMetadata) else None
    safe = _tool_projection(tool)
    return (
        _status(event),
        _proposal_id(event.metadata),
        question.options if question else (),
        question.allow_custom_answer if question else False,
        answer.question_id if answer else None,
        message.client_message_id if message else None,
        question.question_kind if question else None,
        tool.tool if tool else None,
        tool.status if tool else None,
        safe.get("artifact_id"),
        safe.get("filename"),
        safe.get("mime_type"),
        safe.get("schema_name"),
        safe.get("endpoint_risk"),
        safe.get("executed_statements"),
        safe.get("succeeded_statements"),
        safe.get("failed_statements"),
        safe.get("total_duration_ms"),
    )


def _status(event: SessionEvent) -> AgentResultStatus | None:
    metadata = event.metadata
    return metadata.status if isinstance(metadata, AgentResultMetadata) else None


def _proposal_id(metadata: object) -> UUID | None:
    if isinstance(metadata, MessageMetadata):
        return metadata.proposal_change_id
    if not isinstance(metadata, AgentResultMetadata) or not metadata.output_data:
        return None
    try:
        return UUID(metadata.output_data)
    except ValueError:
        return None


def _tool_projection(metadata: ToolResultMetadata | None) -> dict:
    if metadata is None or not metadata.result_data:
        return {}
    value = safe_json_loads(metadata.result_data)
    return value if isinstance(value, dict) else {}
