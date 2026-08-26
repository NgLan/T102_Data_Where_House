"""Pure guards for item-scoped Source Confirmation persistence."""

from src.application.data_warehouse_workflows.input import ResolveSourceCoverageInput
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.analytical_requirement.enums import (
    SourceConfirmationStatus,
    SourceCoverageResolutionAction,
    SourceCoverageStatus,
)
from src.domain.analytical_requirement.source_coverage import SourceCoverageAssessment
from src.domain.project.entities import Project
from src.domain.shared.types import EntityID


def ensure_current_resolution(
    project: Project,
    assessment: SourceCoverageAssessment,
    data: ResolveSourceCoverageInput,
) -> None:
    stale = (
        project.is_requirement_analysis_outdated()
        or project.is_source_coverage_outdated()
        or project.source_revision != data.expected_source_revision
        or assessment.evaluated_source_revision != project.source_revision
        or assessment.batch_id != data.batch_id
    )
    if stale:
        raise BusinessException(ErrorCode.ANALYSIS_INPUT_CHANGED, "Confirmation batch đã cũ.")
    if assessment.status is not SourceCoverageStatus.NEEDS_SOURCE_CONFIRMATION:
        raise BusinessException(ErrorCode.BAD_REQUEST, "Assessment không chờ xác nhận source.")
    if assessment.resolution_revision != data.expected_resolution_revision:
        raise BusinessException(ErrorCode.ANALYSIS_INPUT_CHANGED, "Confirmation item đã thay đổi.")
    if assessment.applied_source_revision is not None:
        raise BusinessException(ErrorCode.BAD_REQUEST, "Batch đã bắt đầu kiểm tra lại.")


def resolution_value(
    assessment: SourceCoverageAssessment,
    data: ResolveSourceCoverageInput,
) -> tuple[SourceConfirmationStatus, EntityID | None]:
    if data.action is SourceCoverageResolutionAction.REJECT_ALL_CANDIDATES:
        if data.candidate_id is not None:
            raise BusinessException(ErrorCode.BAD_REQUEST, "Reject-all không nhận candidate ID.")
        return SourceConfirmationStatus.REJECTED, None
    candidate = next((item for item in assessment.candidates if item.id == data.candidate_id), None)
    if candidate is None:
        raise BusinessException(ErrorCode.BAD_REQUEST, "Candidate không thuộc assessment.")
    return SourceConfirmationStatus.CONFIRMED, candidate.id
