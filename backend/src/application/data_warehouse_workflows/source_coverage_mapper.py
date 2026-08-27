"""Map grounded Source Coverage output vào Analytical Requirement entities."""

from dataclasses import dataclass

from src.application.requirements.output import (
    GeneratedSourceCoverageAssessment,
    GeneratedSourceCoverageCandidate,
    SourceCoverageOutcome,
    SourceCoverageResult,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.utils.uuid import generate_uuid
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.analytical_requirement.source_coverage import (
    SourceCoverageAssessment,
)
from src.domain.analytical_requirement.source_coverage_candidate import (
    SourceCoverageCandidate,
    SourceCoverageReference,
)
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class SourceCoveragePersistenceContext:
    """Identity của batch được gắn atomically vào toàn bộ assessments."""

    batch_id: EntityID
    source_revision: int


def apply_source_coverage(
    result: SourceCoverageResult,
    analytical: tuple[AnalyticalRequirement, ...],
    context: SourceCoveragePersistenceContext,
) -> tuple[AnalyticalRequirement, ...]:
    """Gắn coverage vào đúng canonical Analytical Requirement."""
    by_id = {item.id: item for item in analytical}
    _validate_outcomes(result, by_id)
    for outcome in result.outcomes:
        _apply_outcome(outcome, by_id, context)
    return analytical


def _validate_outcomes(
    result: SourceCoverageResult,
    by_id: dict[EntityID, AnalyticalRequirement],
) -> None:
    actual = [item.analytical_requirement_id for item in result.outcomes]
    if len(actual) != len(by_id) or set(actual) != set(by_id):
        raise BusinessException(
            ErrorCode.INVALID_ANALYTICAL_REQUIREMENT_REF,
            "Source coverage không khớp Analytical Requirements hiện hành.",
        )


def _apply_outcome(
    outcome: SourceCoverageOutcome,
    by_id: dict[EntityID, AnalyticalRequirement],
    context: SourceCoveragePersistenceContext,
) -> None:
    assessments = tuple(_map_assessment(item, context) for item in outcome.assessments)
    by_id[outcome.analytical_requirement_id].replace_source_coverage(assessments)


def _map_assessment(
    item: GeneratedSourceCoverageAssessment,
    context: SourceCoveragePersistenceContext,
) -> SourceCoverageAssessment:
    return SourceCoverageAssessment(
        id=generate_uuid(),
        batch_id=context.batch_id,
        evaluated_source_revision=context.source_revision,
        status=item.status,
        required_concept_key=item.required_concept_key,
        title=item.title,
        explanation=item.explanation,
        question=item.question,
        question_type=item.question_type,
        candidates=tuple(_map_candidate(value) for value in item.candidates),
    )


def _map_candidate(item: GeneratedSourceCoverageCandidate) -> SourceCoverageCandidate:
    references = tuple(
        SourceCoverageReference(
            value.kind,
            value.source_id,
            value.role_key,
            value.role_label,
            value.table_name,
            value.column_name,
            value.from_column,
            value.to_column,
        )
        for value in item.references
    )
    return SourceCoverageCandidate(generate_uuid(), item.label, references)
