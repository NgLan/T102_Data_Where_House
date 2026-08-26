"""Normalization policy của ProjectSession aggregate."""

from typing import Protocol

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.project_session.enums import (
    RequirementContinuationState,
    SessionPurpose,
    SessionStatus,
)
from src.domain.shared.enum_rules import normalize_str_enum

DEFAULT_SESSION_TITLE = "Untitled Session"


class NormalizableSession(Protocol):
    title: str
    status: SessionStatus
    purpose: SessionPurpose
    base_requirement_revision: int | None
    requirement_continuation_state: RequirementContinuationState


def normalize_project_session(session: NormalizableSession) -> None:
    """Chuẩn hóa enum/title và bảo vệ Requirement session base revision."""
    session.title = (session.title or DEFAULT_SESSION_TITLE).strip()
    session.status = normalize_str_enum(
        session.status, SessionStatus, ErrorCode.VALIDATION_ERROR
    )
    session.purpose = normalize_str_enum(
        session.purpose, SessionPurpose, ErrorCode.VALIDATION_ERROR
    )
    session.requirement_continuation_state = normalize_str_enum(
        session.requirement_continuation_state,
        RequirementContinuationState,
        ErrorCode.VALIDATION_ERROR,
    )
    if session.purpose is SessionPurpose.REQUIREMENT_CLARIFICATION and (
        session.base_requirement_revision is None
    ):
        raise BusinessException(
            ErrorCode.VALIDATION_ERROR,
            "Requirement clarification session phải có base revision.",
        )
