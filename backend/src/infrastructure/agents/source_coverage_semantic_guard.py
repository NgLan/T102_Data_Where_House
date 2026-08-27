"""Deterministic guards for USER-confirmed Source Coverage semantics."""

from dataclasses import dataclass
from uuid import UUID

from src.application.requirements.output import (
    GeneratedSourceCoverageAssessment,
    GeneratedSourceCoverageCandidate,
    GeneratedSourceCoverageReference,
)
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.data_source.entities import DataSource
from src.domain.data_source.enums import SourceSemanticDecision
from src.domain.data_source.semantic_metadata import SourceSemanticAnnotation
from src.domain.data_source.value_objects import SchemaMetadata


def reject_repeated_confirmation(
    assessments: tuple[GeneratedSourceCoverageAssessment, ...],
    requirement_id: UUID,
    sources: dict[UUID, DataSource],
) -> None:
    """Từ chối mapping đã xác nhận đầy đủ hoặc reference từng bị USER loại."""
    for assessment in assessments:
        context = _GuardContext(assessment, requirement_id, sources)
        for candidate in assessment.candidates:
            _validate_candidate(context, candidate)


@dataclass(frozen=True, slots=True)
class _GuardContext:
    assessment: GeneratedSourceCoverageAssessment
    requirement_id: UUID
    sources: dict[UUID, DataSource]


def _validate_candidate(
    context: _GuardContext,
    candidate: GeneratedSourceCoverageCandidate,
) -> None:
    annotations = tuple(_matching_annotation(reference, context) for reference in candidate.references)
    if any(item and item.decision is SourceSemanticDecision.REJECTED for item in annotations):
        _raise_semantic_error("Source Coverage trả lại candidate USER đã loại.")
    confirmed = all(item and item.decision is SourceSemanticDecision.CONFIRMED for item in annotations)
    if confirmed and context.assessment.status.value == "NEEDS_SOURCE_CONFIRMATION":
        _raise_semantic_error("Source Coverage hỏi lại mapping đã được USER xác nhận.")


def _matching_annotation(
    reference: GeneratedSourceCoverageReference,
    context: _GuardContext,
) -> SourceSemanticAnnotation | None:
    annotations = _reference_annotations(reference, context.sources)
    return next(
        (
            item
            for item in annotations
            if (
                item.requirement_id == context.requirement_id
                and item.required_concept_key.casefold() == context.assessment.required_concept_key.casefold()
                and (item.role_key or None) == (reference.role_key or None)
            )
        ),
        None,
    )


def _reference_annotations(
    reference: GeneratedSourceCoverageReference,
    sources: dict[UUID, DataSource],
) -> tuple[SourceSemanticAnnotation, ...]:
    source = sources.get(reference.source_id)
    schema = source.schema_metadata if source else None
    if schema is None:
        return ()
    if reference.table_name and reference.column_name:
        return _column_annotations(reference, schema)
    return _relationship_annotations(reference, schema)


def _column_annotations(
    reference: GeneratedSourceCoverageReference,
    schema: SchemaMetadata,
) -> tuple[SourceSemanticAnnotation, ...]:
    return next(
        (
            column.semantic_annotations
            for table in schema.tables
            if table.name == reference.table_name
            for column in table.columns
            if column.name == reference.column_name
        ),
        (),
    )


def _relationship_annotations(
    reference: GeneratedSourceCoverageReference,
    schema: SchemaMetadata,
) -> tuple[SourceSemanticAnnotation, ...]:
    return next(
        (
            item.semantic_annotations
            for item in schema.relationships
            if item.from_column == reference.from_column and item.to_column == reference.to_column
        ),
        (),
    )


def _raise_semantic_error(message: str) -> None:
    raise InfrastructureException(ErrorCode.LLM_STRUCTURED_OUTPUT_ERROR, message)
