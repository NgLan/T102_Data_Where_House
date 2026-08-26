"""Map grounded Source Coverage output vào Analytical Requirement entities."""

from src.application.requirements.output import SourceCoverageResult
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.utils.uuid import generate_uuid
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.analytical_requirement.source_coverage import (
    SourceCoverageAssessment,
    SourceCoverageCandidate,
)
from src.domain.shared.types import EntityID


def apply_source_coverage(
    result: SourceCoverageResult,
    analytical: tuple[AnalyticalRequirement, ...],
    batch_id: EntityID,
    source_revision: int,
) -> tuple[AnalyticalRequirement, ...]:
    """Gắn coverage vào đúng canonical Analytical Requirement."""
    by_id = {item.id: item for item in analytical}
    actual = [item.analytical_requirement_id for item in result.outcomes]
    if len(actual) != len(by_id) or set(actual) != set(by_id):
        raise BusinessException(
            ErrorCode.INVALID_ANALYTICAL_REQUIREMENT_REF,
            "Source coverage không khớp Analytical Requirements hiện hành.",
        )
    for outcome in result.outcomes:
        assessments = tuple(
            SourceCoverageAssessment(
                id=generate_uuid(),
                batch_id=batch_id,
                evaluated_source_revision=source_revision,
                status=item.status,
                required_concept_key=item.required_concept_key,
                title=item.title,
                explanation=item.explanation,
                question=item.question,
                candidates=tuple(
                    SourceCoverageCandidate(
                        generate_uuid(),
                        candidate.kind,
                        candidate.source_id,
                        candidate.table_name,
                        candidate.column_name,
                        candidate.from_column,
                        candidate.to_column,
                    )
                    for candidate in item.candidates
                ),
            )
            for item in outcome.assessments
        )
        by_id[outcome.analytical_requirement_id].replace_source_coverage(assessments)
    return analytical
