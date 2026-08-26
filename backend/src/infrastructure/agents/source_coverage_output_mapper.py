"""Grounding mapper cho Source Coverage structured output."""

from uuid import UUID

from src.application.requirements.input import EvaluateSourceCoverageInput
from src.application.requirements.output import (
    GeneratedSourceCoverageAssessment,
    GeneratedSourceCoverageCandidate,
    SourceCoverageOutcome,
    SourceCoverageResult,
)
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.analytical_requirement.enums import SourceCandidateKind
from src.domain.data_source.entities import DataSource
from src.infrastructure.agents.source_coverage_semantic_guard import (
    reject_repeated_confirmation,
)
from src.infrastructure.llm.source_coverage_structured_outputs import (
    SourceCoverageCandidateItem,
    SourceCoverageLlmResult,
)


def map_source_coverage_result(
    result: SourceCoverageLlmResult,
    data: EvaluateSourceCoverageInput,
) -> SourceCoverageResult:
    """Từ chối analytical ID hoặc source candidate không thuộc canonical input."""
    expected = {item.id for item in data.analytical_requirements}
    actual = [item.analytical_requirement_id for item in result.outcomes]
    if len(actual) != len(expected) or set(actual) != expected:
        _raise_ungrounded("Source Coverage trả thiếu, trùng hoặc sai analytical ID.")
    sources = {item.id: item for item in data.data_sources}
    requirements = {
        item.id: item.requirement_id for item in data.analytical_requirements
    }
    outcomes = []
    for outcome in result.outcomes:
        assessments = tuple(
            GeneratedSourceCoverageAssessment(
                item.status,
                item.required_concept_key,
                item.title,
                item.explanation,
                item.question,
                tuple(_map_candidate(candidate, sources) for candidate in item.candidates),
            )
            for item in outcome.assessments
        )
        reject_repeated_confirmation(
            assessments, requirements[outcome.analytical_requirement_id], sources
        )
        outcomes.append(SourceCoverageOutcome(outcome.analytical_requirement_id, assessments))
        keys = [item.required_concept_key.casefold() for item in assessments]
        if len(keys) != len(set(keys)):
            _raise_ungrounded("Source Coverage trả required_concept_key bị trùng.")
    return SourceCoverageResult(tuple(outcomes))


def _map_candidate(
    item: SourceCoverageCandidateItem,
    sources: dict[UUID, DataSource],
) -> GeneratedSourceCoverageCandidate:
    source_id = item.source_id
    source = sources.get(source_id)
    if source is None or source.schema_metadata is None:
        _raise_ungrounded("Source Coverage trả candidate từ source không tồn tại.")
    if item.kind is SourceCandidateKind.COLUMN:
        _require_column(source, item.table_name or "", item.column_name or "")
    else:
        _require_relationship(source, item.from_column or "", item.to_column or "")
    return GeneratedSourceCoverageCandidate(
        item.kind,
        source_id,
        item.table_name,
        item.column_name,
        item.from_column,
        item.to_column,
    )


def _require_column(source: DataSource, table_name: str, column_name: str) -> None:
    schema = source.schema_metadata
    found = bool(
        schema
        and any(
            table.name == table_name
            and any(column.name == column_name for column in table.columns)
            for table in schema.tables
        )
    )
    if not found:
        _raise_ungrounded("Source Coverage trả column candidate không tồn tại.")


def _require_relationship(
    source: DataSource, from_column: str, to_column: str
) -> None:
    schema = source.schema_metadata
    found = bool(
        schema
        and any(
            item.from_column == from_column and item.to_column == to_column
            for item in schema.relationships
        )
    )
    if not found:
        _raise_ungrounded("Source Coverage trả relationship candidate không tồn tại.")


def _raise_ungrounded(message: str) -> None:
    raise InfrastructureException(ErrorCode.LLM_STRUCTURED_OUTPUT_ERROR, message)
