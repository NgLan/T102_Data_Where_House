"""Domain entity cho immutable Agent session event."""

from dataclasses import dataclass

from src.common.exceptions.error_codes import ErrorCode
from src.domain.project_session.enums import SessionEventRole, SessionEventType
from src.domain.project_session.rules import (
    validate_session_event_ref,
    validate_session_event_shape,
    validate_session_metadata,
)
from src.domain.project_session.value_objects import SessionEventMetadata
from src.domain.shared.entity import BaseEntity
from src.domain.shared.enum_rules import normalize_str_enum
from src.domain.shared.types import EntityID


@dataclass(eq=False, kw_only=True)
class SessionEvent(BaseEntity):
    """Sự kiện audit hoặc conversational thuộc một ProjectSession."""

    session_id: EntityID
    role: SessionEventRole = SessionEventRole.USER
    type: SessionEventType = SessionEventType.MESSAGE
    content: str | None = None
    metadata: SessionEventMetadata | None = None
    turn_id: EntityID | None = None

    def __post_init__(self) -> None:
        """Chuẩn hóa shape và metadata trước khi event được persist."""
        super().__post_init__()
        self.role = normalize_str_enum(
            self.role, SessionEventRole, ErrorCode.VALIDATION_ERROR
        )
        self.type = normalize_str_enum(
            self.type, SessionEventType, ErrorCode.VALIDATION_ERROR
        )
        self.content = self.content.strip() if self.content is not None else None
        validate_session_event_ref(self.session_id)
        validate_session_event_shape(self.role, self.type, self.content)
        validate_session_metadata(self.type, self.metadata)
