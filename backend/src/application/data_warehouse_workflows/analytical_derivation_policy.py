"""Policy chặn workflow theo outcome của Analytical Requirement derivation."""

from src.application.requirements.input import RequirementContext
from src.application.requirements.output import (
    AnalyticalDerivationOutcome,
    AnalyticalDerivationResult,
    AnalyticalDerivationStatus,
    GeneratedAnalyticalRequirement,
)
from src.common.exceptions.base import ExceptionDetail
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode


def require_ready_derivation(
    result: AnalyticalDerivationResult,
    requirements: tuple[RequirementContext, ...],
) -> tuple[GeneratedAnalyticalRequirement, ...]:
    """Trả output READY hoặc dừng đúng loại thiếu hụt có truy vết."""
    semantic_gaps = _by_status(result, AnalyticalDerivationStatus.NEEDS_REQUIREMENT_CLARIFICATION)
    if semantic_gaps:
        raise _blocked(
            ErrorCode.REQUIREMENT_SEMANTIC_CLARIFICATION_REQUIRED,
            "Requirement còn quyết định nghiệp vụ cần làm rõ.",
            semantic_gaps,
        )
    return tuple(item for outcome in result.outcomes for item in outcome.analytical_requirements)


def _by_status(
    result: AnalyticalDerivationResult, status: AnalyticalDerivationStatus
) -> tuple[AnalyticalDerivationOutcome, ...]:
    return tuple(item for item in result.outcomes if item.status == status)


def _blocked(
    code: ErrorCode,
    message: str,
    outcomes: tuple[AnalyticalDerivationOutcome, ...],
) -> BusinessException:
    details = tuple(ExceptionDetail(str(item.source_requirement_id), item.reason or message) for item in outcomes)
    return BusinessException(code, message, details)
