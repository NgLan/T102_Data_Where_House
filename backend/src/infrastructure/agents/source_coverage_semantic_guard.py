"""Deterministic guards for USER-confirmed Source Coverage semantics."""

from uuid import UUID

from src.application.requirements.output import GeneratedSourceCoverageAssessment
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.data_source.entities import DataSource
from src.domain.data_source.enums import SourceSemanticDecision
from src.domain.data_source.semantic_metadata import SourceSemanticAnnotation


def reject_repeated_confirmation(
    assessments: tuple[GeneratedSourceCoverageAssessment, ...],
    requirement_id: UUID,
    sources: dict[UUID, DataSource],
) -> None:
    """Reject an LLM result that asks for an already confirmed scoped concept."""
    annotations = _annotations(sources)
    for assessment in assessments:
        confirmed = any(
            item.requirement_id == requirement_id
            and item.required_concept_key.casefold()
            == assessment.required_concept_key.casefold()
            and item.decision is SourceSemanticDecision.CONFIRMED
            for item in annotations
        )
        if confirmed and assessment.status.value == "NEEDS_SOURCE_CONFIRMATION":
            raise InfrastructureException(
                ErrorCode.LLM_STRUCTURED_OUTPUT_ERROR,
                "Source Coverage hỏi lại concept đã được USER xác nhận.",
            )


def _annotations(
    sources: dict[UUID, DataSource],
) -> tuple[SourceSemanticAnnotation, ...]:
    columns = tuple(
        annotation
        for source in sources.values()
        if source.schema_metadata
        for table in source.schema_metadata.tables
        for column in table.columns
        for annotation in column.semantic_annotations
    )
    relationships = tuple(
        annotation
        for source in sources.values()
        if source.schema_metadata
        for relationship in source.schema_metadata.relationships
        for annotation in relationship.semantic_annotations
    )
    return (*columns, *relationships)
