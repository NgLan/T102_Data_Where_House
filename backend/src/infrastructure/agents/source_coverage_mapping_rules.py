"""Deterministic uniqueness rules cho grounded Source Coverage output."""

from src.application.requirements.output import (
    GeneratedSourceCoverageAssessment,
    GeneratedSourceCoverageCandidate,
)
from src.infrastructure.llm.structured_output_models import (
    StructuredOutputFailureCategory as Category,
)
from src.infrastructure.llm.structured_output_models import (
    StructuredOutputIssue,
    StructuredOutputItemError,
)


def ensure_unique_candidates(
    candidates: tuple[GeneratedSourceCoverageCandidate, ...],
    reference: str,
) -> None:
    """Từ chối candidate trùng exact grounded reference signature."""
    signatures = [_candidate_signature(value) for value in candidates]
    if len(signatures) != len(set(signatures)):
        _raise_item("Duplicate candidate mapping.", reference)


def ensure_unique_assessments(
    assessments: tuple[GeneratedSourceCoverageAssessment, ...],
    reference: str,
) -> None:
    """Từ chối required concept lặp trong cùng analytical outcome."""
    keys = [item.required_concept_key.casefold() for item in assessments]
    if len(keys) != len(set(keys)):
        _raise_item("Duplicate concept key.", reference)


def _candidate_signature(
    candidate: GeneratedSourceCoverageCandidate,
) -> tuple[object, ...]:
    return tuple(
        (
            item.kind,
            item.source_id,
            item.role_key,
            item.table_name,
            item.column_name,
            item.from_column,
            item.to_column,
        )
        for item in candidate.references
    )


def _raise_item(message: str, reference: str) -> None:
    raise StructuredOutputItemError(StructuredOutputIssue(Category.SEMANTIC_FIELD_MISSING, message, reference))
