"""Ground Source Coverage references bằng canonical metadata index."""

from dataclasses import dataclass

from src.application.requirements.output import (
    GeneratedSourceCoverageCandidate,
    GeneratedSourceCoverageReference,
)
from src.domain.analytical_requirement.enums import SourceCandidateKind
from src.domain.shared.types import EntityID
from src.infrastructure.agents.schema_metadata_index import SchemaMetadataIndex
from src.infrastructure.llm.source_coverage_structured_outputs import (
    SourceCoverageCandidateItem,
    SourceCoverageReferenceItem,
)
from src.infrastructure.llm.structured_output_models import (
    StructuredOutputFailureCategory as Category,
)
from src.infrastructure.llm.structured_output_models import (
    StructuredOutputIssue,
    StructuredOutputItemError,
)


def map_grounded_candidate(
    item: SourceCoverageCandidateItem,
    index: SchemaMetadataIndex,
    outcome_ref: str,
) -> GeneratedSourceCoverageCandidate:
    """Map candidate chỉ khi mọi source reference tồn tại chính xác."""
    references = tuple(_map_reference(reference, index, outcome_ref) for reference in item.references)
    return GeneratedSourceCoverageCandidate(item.label, references)


def _map_reference(
    item: SourceCoverageReferenceItem,
    index: SchemaMetadataIndex,
    outcome_ref: str,
) -> GeneratedSourceCoverageReference:
    source_id = index.source_id(item.source_ref)
    if source_id is None:
        _raise(outcome_ref, _Failure(Category.SOURCE_REF_UNKNOWN, "source_ref", "Unknown source_ref."))
    if item.kind is SourceCandidateKind.COLUMN:
        _validate_column(item, index, outcome_ref)
    else:
        _validate_relationship(item, index, outcome_ref)
    return _to_output(item, source_id)


def _to_output(
    item: SourceCoverageReferenceItem,
    source_id: EntityID,
) -> GeneratedSourceCoverageReference:
    return GeneratedSourceCoverageReference(
        item.kind,
        source_id,
        item.role_key,
        item.role_label,
        item.table_name,
        item.column_name,
        item.from_column,
        item.to_column,
    )


def _validate_column(
    item: SourceCoverageReferenceItem,
    index: SchemaMetadataIndex,
    outcome_ref: str,
) -> None:
    table_name, column_name = item.table_name or "", item.column_name or ""
    if not index.has_table(item.source_ref, table_name):
        _raise(
            outcome_ref,
            _Failure(
                Category.SOURCE_TABLE_UNKNOWN,
                "table_name",
                "Table does not exist in canonical metadata.",
            ),
        )
    if not index.has_column(item.source_ref, table_name, column_name):
        columns = ", ".join(index.columns_for(item.source_ref, table_name))
        message = f"Column does not exist. Valid columns: {columns}" if columns else "Column does not exist."
        _raise(
            outcome_ref,
            _Failure(Category.SOURCE_COLUMN_UNKNOWN, "column_name", message),
        )


def _validate_relationship(
    item: SourceCoverageReferenceItem,
    index: SchemaMetadataIndex,
    reference: str,
) -> None:
    if index.has_relationship(item.source_ref, item.from_column or "", item.to_column or ""):
        return
    _raise(
        reference,
        _Failure(
            Category.SOURCE_RELATIONSHIP_UNKNOWN,
            "references",
            "Relationship does not exist in canonical metadata.",
        ),
    )


@dataclass(frozen=True, slots=True)
class _Failure:
    category: Category
    field: str
    message: str


def _raise(reference: str, failure: _Failure) -> None:
    raise StructuredOutputItemError(
        StructuredOutputIssue(
            failure.category,
            failure.message,
            reference,
            failure.field,
        )
    )
