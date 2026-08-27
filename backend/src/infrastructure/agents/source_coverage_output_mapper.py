"""Validate identity và map grounded Source Coverage output."""

from dataclasses import dataclass

from src.application.requirements.input import EvaluateSourceCoverageInput
from src.application.requirements.output import (
    GeneratedSourceCoverageAssessment,
    SourceCoverageOutcome,
    SourceCoverageResult,
)
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.infrastructure.agents.schema_metadata_index import SchemaMetadataIndex
from src.infrastructure.agents.source_coverage_grounding import map_grounded_candidate
from src.infrastructure.agents.source_coverage_mapping_rules import (
    ensure_unique_assessments,
    ensure_unique_candidates,
)
from src.infrastructure.agents.source_coverage_semantic_guard import reject_repeated_confirmation
from src.infrastructure.agents.transport_references import (
    SourceCoverageReferenceBoundary,
    TransportReferenceMap,
)
from src.infrastructure.llm.source_coverage_structured_outputs import (
    SourceCoverageAssessmentItem,
    SourceCoverageLlmResult,
    SourceCoverageOutcomeItem,
)
from src.infrastructure.llm.structured_output_models import (
    StructuredOutputFailureCategory as Category,
)
from src.infrastructure.llm.structured_output_models import (
    StructuredOutputIssue,
    StructuredOutputItemError,
)


def map_source_coverage_result(
    result: SourceCoverageLlmResult,
    data: EvaluateSourceCoverageInput,
) -> SourceCoverageResult:
    """Map complete result hoặc trả public structured-output error."""
    references = SourceCoverageReferenceBoundary(
        TransportReferenceMap.create("R", tuple(item.id for item in data.requirements)),
        TransportReferenceMap.create("A", tuple(item.id for item in data.analytical_requirements)),
        TransportReferenceMap.create("S", tuple(item.id for item in data.data_sources)),
    )
    context = SourceCoverageMappingContext.create(data, references)
    actual = [item.analytical_requirement_ref for item in result.outcomes]
    expected = set(references.analytical_requirements.references)
    if len(actual) != len(expected) or set(actual) != expected:
        _raise_public("Source Coverage trả thiếu, trùng hoặc sai analytical ref.")
    try:
        outcomes = tuple(map_source_coverage_outcome(item, context) for item in result.outcomes)
    except StructuredOutputItemError as exc:
        raise InfrastructureException(
            ErrorCode.LLM_STRUCTURED_OUTPUT_ERROR,
            exc.issue.message,
        ) from exc
    return SourceCoverageResult(outcomes)


def map_source_coverage_outcome(
    item: SourceCoverageOutcomeItem,
    context: "SourceCoverageMappingContext",
) -> SourceCoverageOutcome:
    """Ground một independent analytical outcome."""
    analytical_id = context.references.analytical_requirements.resolve(item.analytical_requirement_ref)
    if analytical_id is None:
        raise StructuredOutputItemError(
            StructuredOutputIssue(
                Category.ANALYTICAL_REF_UNKNOWN,
                "Unknown analytical_requirement_ref.",
                item.analytical_requirement_ref,
            )
        )
    assessments = tuple(
        _map_assessment(value, context.index, item.analytical_requirement_ref) for value in item.assessments
    )
    ensure_unique_assessments(assessments, item.analytical_requirement_ref)
    requirements = {value.id: value.requirement_id for value in context.data.analytical_requirements}
    sources = {value.id: value for value in context.data.data_sources}
    reject_repeated_confirmation(assessments, requirements[analytical_id], sources)
    return SourceCoverageOutcome(analytical_id, assessments)


def _map_assessment(
    item: SourceCoverageAssessmentItem,
    index: SchemaMetadataIndex,
    outcome_ref: str,
) -> GeneratedSourceCoverageAssessment:
    candidates = tuple(map_grounded_candidate(value, index, outcome_ref) for value in item.candidates)
    ensure_unique_candidates(candidates, outcome_ref)
    return GeneratedSourceCoverageAssessment(
        item.status,
        item.required_concept_key,
        item.title,
        item.explanation,
        item.question,
        item.question_type,
        candidates,
    )


def _raise_public(message: str) -> None:
    raise InfrastructureException(ErrorCode.LLM_STRUCTURED_OUTPUT_ERROR, message)


@dataclass(frozen=True, slots=True)
class SourceCoverageMappingContext:
    """Canonical data và indexes dùng lại khi map nhiều outcome."""

    data: EvaluateSourceCoverageInput
    references: SourceCoverageReferenceBoundary
    index: SchemaMetadataIndex

    @classmethod
    def create(
        cls,
        data: EvaluateSourceCoverageInput,
        references: SourceCoverageReferenceBoundary,
    ) -> "SourceCoverageMappingContext":
        """Tạo exact metadata index một lần cho toàn invocation."""
        index = SchemaMetadataIndex.create(data.data_sources, references.sources)
        return cls(data, references, index)
