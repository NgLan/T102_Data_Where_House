"""Pure guards and candidate lookup for Source Coverage batch recheck."""

from src.application.data_warehouse_workflows.input import RecheckSourceCoverageInput
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.analytical_requirement.enums import (
    SourceConfirmationStatus,
    SourceCoverageStatus,
)
from src.domain.analytical_requirement.source_coverage import SourceCoverageAssessment
from src.domain.analytical_requirement.source_coverage_candidate import (
    SourceCoverageCandidate,
    SourceCoverageReference,
)
from src.domain.data_source.entities import DataSource
from src.domain.project.entities import Project


def ensure_recheckable(
    project: Project,
    assessments: tuple[SourceCoverageAssessment, ...],
    data: RecheckSourceCoverageInput,
) -> bool:
    confirmations = _confirmations(assessments)
    if not confirmations or any(item.batch_id != data.batch_id for item in assessments):
        raise BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "Confirmation batch không tồn tại.")
    if project.source_revision != data.expected_source_revision:
        raise BusinessException(ErrorCode.ANALYSIS_INPUT_CHANGED, "Source revision đã thay đổi.")
    if all(item.applied_source_revision == project.source_revision for item in confirmations):
        return False
    stale = project.is_requirement_analysis_outdated() or project.is_source_coverage_outdated()
    if stale or any(item.evaluated_source_revision != project.source_revision for item in assessments):
        raise BusinessException(ErrorCode.ANALYSIS_INPUT_CHANGED, "Confirmation batch đã cũ.")
    if any(item.confirmation_status is SourceConfirmationStatus.PENDING for item in confirmations):
        raise BusinessException(ErrorCode.BAD_REQUEST, "Batch còn nội dung chưa được xử lý.")
    return True


def resolution_candidates(
    assessment: SourceCoverageAssessment,
) -> tuple[SourceCoverageCandidate, ...]:
    if assessment.confirmation_status is SourceConfirmationStatus.REJECTED:
        return assessment.candidates
    selected = tuple(item for item in assessment.candidates if item.id == assessment.selected_candidate_id)
    if len(selected) != 1:
        raise BusinessException(ErrorCode.BAD_REQUEST, "Candidate đã chọn không hợp lệ.")
    return selected


def apply_reference(
    sources: dict[object, DataSource],
    reference: SourceCoverageReference,
    annotation: object,
) -> None:
    source = sources.get(reference.source_id)
    if source is None:
        raise BusinessException(ErrorCode.ANALYSIS_INPUT_CHANGED, "Source candidate đã thay đổi.")
    if reference.table_name and reference.column_name:
        applied = source.annotate_column(reference.table_name, reference.column_name, annotation)
    else:
        applied = source.annotate_relationship(reference.from_column or "", reference.to_column or "", annotation)
    if not applied:
        raise BusinessException(ErrorCode.ANALYSIS_INPUT_CHANGED, "Source candidate đã thay đổi.")


def _confirmations(
    assessments: tuple[SourceCoverageAssessment, ...],
) -> tuple[SourceCoverageAssessment, ...]:
    return tuple(item for item in assessments if item.status is SourceCoverageStatus.NEEDS_SOURCE_CONFIRMATION)
