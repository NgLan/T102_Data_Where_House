"""Thực thể thuộc miền Phiên Agent (Project Session Entities)."""

from dataclasses import dataclass
from datetime import datetime

from src.common.exceptions.error_codes import ErrorCode
from src.domain.project_session.enums import SessionEventRole, SessionEventType, SessionStatus
from src.domain.project_session.rules import (
    validate_session_event_ref,
    validate_session_event_shape,
    validate_session_metadata,
)
from src.domain.project_session.value_objects import SessionEventMetadata
from src.domain.shared.entity import BaseEntity
from src.domain.shared.enum_rules import normalize_str_enum
from src.domain.shared.types import EntityID

DEFAULT_SESSION_TITLE = "Untitled Session"


@dataclass(eq=False, kw_only=True)
class ProjectSession(BaseEntity):
    """Thực thể đại diện cho Phiên làm việc Dự án (Project Session)."""

    project_id: EntityID
    user_id: EntityID
    title: str = DEFAULT_SESSION_TITLE
    status: SessionStatus = SessionStatus.ACTIVE
    active_turn_id: EntityID | None = None
    active_turn_started_at: datetime | None = None

    def __post_init__(self) -> None:
        """Chuẩn hóa tiêu đề, trạng thái và timestamp của phiên."""
        super().__post_init__()
        self.title = (self.title or DEFAULT_SESSION_TITLE).strip()
        self.status = normalize_str_enum(self.status, SessionStatus, ErrorCode.VALIDATION_ERROR)

    def acquire_turn(self, turn_id: EntityID, stale_before: datetime) -> None:
        """Giữ khóa một lượt Agent, cho phép thay lượt đã quá hạn."""
        if self.active_turn_id and self.active_turn_started_at:
            if self.active_turn_started_at >= stale_before:
                from src.common.exceptions.business import BusinessException

                raise BusinessException(
                    ErrorCode.SESSION_RUN_IN_PROGRESS,
                    "Phiên đang có một lượt Agent được xử lý.",
                )
        from src.common.utils.datetime import utc_now

        self.active_turn_id = turn_id
        self.active_turn_started_at = utc_now()
        self.mark_updated()

    def release_turn(self, turn_id: EntityID) -> None:
        """Giải phóng đúng lượt Agent hiện hành."""
        if self.active_turn_id != turn_id:
            return
        self.active_turn_id = None
        self.active_turn_started_at = None
        self.mark_updated()

    def rename(self, title: str) -> None:
        """Rename a session with a non-empty user-facing title."""
        normalized = title.strip()
        if not normalized:
            from src.common.exceptions.business import BusinessException

            raise BusinessException(ErrorCode.VALIDATION_ERROR, "Session title is required.")
        self.title = normalized
        self.mark_updated()


@dataclass(eq=False, kw_only=True)
class SessionEvent(BaseEntity):
    """Thực thể đại diện cho Sự kiện trong Phiên (Session Event)."""

    session_id: EntityID
    role: SessionEventRole = SessionEventRole.USER
    type: SessionEventType = SessionEventType.MESSAGE
    content: str | None = None
    metadata: SessionEventMetadata | None = None
    turn_id: EntityID | None = None

    def __post_init__(self) -> None:
        """Kiểm tra quy tắc nghiệp vụ cho SessionEvent và đảm bảo timezone UTC."""
        super().__post_init__()
        self.role = normalize_str_enum(self.role, SessionEventRole, ErrorCode.VALIDATION_ERROR)
        self.type = normalize_str_enum(self.type, SessionEventType, ErrorCode.VALIDATION_ERROR)
        self.content = self.content.strip() if self.content is not None else None
        validate_session_event_ref(self.session_id)
        validate_session_event_shape(self.role, self.type, self.content)
        validate_session_metadata(self.type, self.metadata)
