"""Codec nghiêm ngặt cho derived source coverage JSONB."""

from uuid import UUID

from pydantic import TypeAdapter, ValidationError
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.analytical_requirement.source_coverage import (
    SourceCoverageAssessment,
    SourceCoverageCandidate,
)
from src.domain.shared.types import JsonValue
from src.infrastructure.database.mappers.source_coverage_records import (
    SourceCoverageAssessmentRecord,
    SourceCoverageCandidateRecord,
)

_RECORDS = TypeAdapter(list[SourceCoverageAssessmentRecord])


def encode_source_coverage(
    assessments: tuple[SourceCoverageAssessment, ...],
) -> list[JsonValue]:
    """Chuyển domain assessments sang JSONB primitives."""
    records = [_assessment_to_record(item) for item in assessments]
    return _RECORDS.dump_python(records, mode="json")


def decode_source_coverage(payload: object) -> tuple[SourceCoverageAssessment, ...]:
    """Khôi phục assessments và báo database error khi payload hỏng."""
    try:
        records = _RECORDS.validate_python(payload or [])
        return tuple(_record_to_assessment(item) for item in records)
    except (ValidationError, BusinessException) as exc:
        raise InfrastructureException(
            ErrorCode.DATABASE_ERROR,
            "Source coverage metadata trong cơ sở dữ liệu không hợp lệ.",
        ) from exc


def _assessment_to_record(
    assessment: SourceCoverageAssessment,
) -> SourceCoverageAssessmentRecord:
    return SourceCoverageAssessmentRecord(
        id=assessment.id,
        batch_id=assessment.batch_id,
        evaluated_source_revision=assessment.evaluated_source_revision,
        status=assessment.status,
        required_concept_key=assessment.required_concept_key,
        title=assessment.title,
        explanation=assessment.explanation,
        question=assessment.question,
        confirmation_status=assessment.confirmation_status,
        selected_candidate_id=assessment.selected_candidate_id,
        resolution_revision=assessment.resolution_revision,
        applied_source_revision=assessment.applied_source_revision,
        candidates=[_candidate_to_record(item) for item in assessment.candidates],
    )


def _candidate_to_record(
    candidate: SourceCoverageCandidate,
) -> SourceCoverageCandidateRecord:
    return SourceCoverageCandidateRecord.model_validate(candidate, from_attributes=True)


def _record_to_assessment(
    record: SourceCoverageAssessmentRecord,
) -> SourceCoverageAssessment:
    return SourceCoverageAssessment(
        id=record.id,
        batch_id=record.batch_id or UUID(int=0),
        evaluated_source_revision=record.evaluated_source_revision,
        status=record.status,
        required_concept_key=record.required_concept_key,
        title=record.title,
        explanation=record.explanation,
        question=record.question or (
            record.title
            if record.status.value == "NEEDS_SOURCE_CONFIRMATION"
            else None
        ),
        confirmation_status=record.confirmation_status,
        selected_candidate_id=record.selected_candidate_id,
        resolution_revision=record.resolution_revision,
        applied_source_revision=record.applied_source_revision,
        candidates=tuple(
            SourceCoverageCandidate(**item.model_dump()) for item in record.candidates
        ),
    )
