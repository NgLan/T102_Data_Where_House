"""Thực thể thuộc miền Phiên Agent (Project Session Entities)."""

from dataclasses import dataclass
from datetime import datetime

from src.common.exceptions.error_codes import ErrorCode
from src.domain.project_session.conversation_summary import (
    ConversationSummary,
    ConversationSummaryUpdate,
    apply_summary_update,
)
from src.domain.project_session.enums import (
    RequirementContinuationState,
    SessionPurpose,
    SessionStatus,
)
from src.domain.project_session.requirement_continuation import (
    RequirementContinuationMixin,
)
from src.domain.project_session.session_event import SessionEvent as SessionEvent
from src.domain.project_session.session_lifecycle import (
    archive_session,
    complete_session,
    rename_session,
)
from src.domain.project_session.session_normalization import (
    DEFAULT_SESSION_TITLE,
    normalize_project_session,
)
from src.domain.shared.entity import BaseEntity
from src.domain.shared.types import EntityID


@dataclass(eq=False, kw_only=True)
class ProjectSession(BaseEntity, RequirementContinuationMixin):
    """Thực thể đại diện cho Phiên làm việc Dự án (Project Session)."""

    project_id: EntityID
    user_id: EntityID
    title: str = DEFAULT_SESSION_TITLE
    status: SessionStatus = SessionStatus.ACTIVE
    purpose: SessionPurpose = SessionPurpose.DATA_MODELING
    base_requirement_revision: int | None = None
    requirement_continuation_state: RequirementContinuationState = (
        RequirementContinuationState.NOT_REQUIRED
    )
    active_turn_id: EntityID | None = None
    active_turn_started_at: datetime | None = None
    pending_question_id: EntityID | None = None
    conversation_summary: ConversationSummary | None = None
    summarized_through_event_id: EntityID | None = None
    summary_updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """Chuẩn hóa tiêu đề, trạng thái và timestamp của phiên."""
        super().__post_init__()
        normalize_project_session(self)

    def acquire_turn(self, turn_id: EntityID, stale_before: datetime) -> None:
        """Giữ khóa một lượt Agent, cho phép thay lượt đã quá hạn."""
        if self.pending_question_id:
            self._raise_pending()
        self._acquire_turn(turn_id, stale_before)

    def resume_turn(self, question_id: EntityID, turn_id: EntityID, stale_before: datetime) -> None:
        """Nhận đúng clarification pending trước khi chạy tiếp lượt cũ."""
        if self.pending_question_id != question_id:
            from src.common.exceptions.business import BusinessException

            raise BusinessException(
                ErrorCode.SESSION_CLARIFICATION_STALE,
                "Clarification không còn chờ câu trả lời.",
            )
        self._acquire_turn(turn_id, stale_before)
        self.pending_question_id = None
        self.mark_updated()

    def wait_for_clarification(self, turn_id: EntityID, question_id: EntityID) -> None:
        """Tạm dừng đúng lượt hiện hành tại một câu hỏi clarification."""
        if self.active_turn_id != turn_id:
            from src.common.exceptions.business import BusinessException

            raise BusinessException(
                ErrorCode.SESSION_CLARIFICATION_STALE,
                "Không thể tạm dừng một Agent turn không còn hoạt động.",
            )
        self.release_turn(turn_id)
        self.pending_question_id = question_id
        self.mark_updated()

    def _acquire_turn(self, turn_id: EntityID, stale_before: datetime) -> None:
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

    @staticmethod
    def _raise_pending() -> None:
        from src.common.exceptions.business import BusinessException

        raise BusinessException(
            ErrorCode.SESSION_CLARIFICATION_PENDING,
            "Phiên đang chờ người dùng trả lời clarification.",
        )

    def release_turn(self, turn_id: EntityID) -> None:
        """Giải phóng đúng lượt Agent hiện hành."""
        if self.active_turn_id != turn_id:
            return
        self.active_turn_id = None
        self.active_turn_started_at = None
        self.mark_updated()

    def apply_conversation_summary(self, update: ConversationSummaryUpdate) -> None:
        """Advance the derived summary checkpoint after concurrency validation."""
        apply_summary_update(self, update)

    def rename(self, title: str) -> None:
        """Rename a session with a non-empty user-facing title."""
        rename_session(self, title)

    def complete(self) -> None:
        """Hoàn tất session khi không còn turn hoặc question pending."""
        complete_session(self)

    def archive(self) -> None:
        """Archive cycle cũ nhưng giữ toàn bộ audit history."""
        archive_session(self)
