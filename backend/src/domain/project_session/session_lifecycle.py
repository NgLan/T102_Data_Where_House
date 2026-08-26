"""Pure lifecycle transitions cho ProjectSession."""

from typing import TYPE_CHECKING

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.project_session.enums import SessionStatus

if TYPE_CHECKING:
    from src.domain.project_session.entities import ProjectSession


def complete_session(session: "ProjectSession") -> None:
    """Hoàn tất session không có turn hoặc pending question."""
    if session.active_turn_id or session.pending_question_id:
        raise BusinessException(
            ErrorCode.SESSION_RUN_IN_PROGRESS,
            "Không thể hoàn tất session đang xử lý clarification.",
        )
    session.status = SessionStatus.COMPLETED
    session.mark_updated()


def archive_session(session: "ProjectSession") -> None:
    """Archive cycle và giải phóng toàn bộ transient lock state."""
    session.active_turn_id = None
    session.active_turn_started_at = None
    session.pending_question_id = None
    session.status = SessionStatus.ARCHIVED
    session.mark_updated()


def rename_session(session: "ProjectSession", title: str) -> None:
    """Rename session bằng title không rỗng."""
    normalized = title.strip()
    if not normalized:
        raise BusinessException(ErrorCode.VALIDATION_ERROR, "Session title is required.")
    session.title = normalized
    session.mark_updated()
