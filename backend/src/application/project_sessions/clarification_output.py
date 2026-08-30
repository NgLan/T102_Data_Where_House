"""Application outputs dành riêng cho clarification đang chờ."""

from dataclasses import dataclass
from datetime import datetime

from src.domain.project_session.clarification import ClarificationQuestionMetadata
from src.domain.project_session.entities import SessionEvent
from src.domain.project_session.enums import SessionEventType, SessionQuestionKind
from src.domain.sandbox.enums import SandboxEndpointRisk
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class ClarificationQuestionOutput:
    """Câu hỏi pending an toàn để xuất qua presentation boundary."""

    question_id: EntityID
    session_id: EntityID
    turn_id: EntityID
    question: str
    options: tuple[str, ...]
    allow_custom_answer: bool
    reason: str | None
    question_kind: SessionQuestionKind
    tool_name: str | None
    endpoint_risk: SandboxEndpointRisk | None
    schema_name: str | None
    reset_schema: bool | None
    created_at: datetime

    @classmethod
    def from_domain(cls, event: SessionEvent) -> "ClarificationQuestionOutput":
        metadata = event.metadata
        if (
            event.type is not SessionEventType.QUESTION
            or not event.turn_id
            or not event.content
            or not isinstance(metadata, ClarificationQuestionMetadata)
        ):
            raise ValueError("Session event is not a structured clarification question.")
        return cls(
            event.id,
            event.session_id,
            event.turn_id,
            event.content,
            metadata.options,
            metadata.allow_custom_answer,
            metadata.reason,
            metadata.question_kind,
            metadata.tool_name,
            metadata.endpoint_risk,
            metadata.schema_name,
            metadata.reset_schema,
            event.created_at,
        )
