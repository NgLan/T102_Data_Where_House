"""Business guards dùng chung cho Requirement clarification commands."""

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.project.entities import Project
from src.domain.project_session.entities import ProjectSession
from src.domain.project_session.enums import (
    RequirementContinuationState,
    SessionPurpose,
    SessionStatus,
)


def ensure_requirement_revision(project: Project, expected: int) -> None:
    """Từ chối command dựa trên Requirement revision cũ."""
    if project.requirement_revision != expected:
        raise BusinessException(
            ErrorCode.REQUIREMENT_REVISION_CONFLICT,
            "Requirement revision không còn hiện hành.",
        )


def ensure_requirement_message_session(
    project: Project, session: ProjectSession | None
) -> None:
    """Chỉ cho follow-up trên current Requirement cycle đã được phép edit."""
    valid = bool(
        session
        and session.project_id == project.id
        and session.purpose is SessionPurpose.REQUIREMENT_CLARIFICATION
        and session.status in {SessionStatus.ACTIVE, SessionStatus.COMPLETED}
        and session.base_requirement_revision == project.requirement_revision
    )
    if not valid:
        raise BusinessException(ErrorCode.SESSION_PURPOSE_MISMATCH, "Sai Requirement session.")
    blocked = {
        RequirementContinuationState.AWAITING_DECISION,
        RequirementContinuationState.CONTINUE_ANALYSIS,
    }
    if session and session.requirement_continuation_state in blocked:
        raise BusinessException(
            ErrorCode.REQUIREMENT_CONTINUATION_INVALID,
            "Hãy hoàn tất continuation gate trước khi gửi tin nhắn.",
        )
