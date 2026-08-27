"""Typed record codec cho SourceSemanticAnnotation."""

from src.domain.data_source.semantic_metadata import SourceSemanticAnnotation
from src.infrastructure.database.mappers.data_source.schema_metadata_records import (
    SemanticAnnotationRecord,
)


def annotation_to_record(
    annotation: SourceSemanticAnnotation,
) -> SemanticAnnotationRecord:
    """Chuyển semantic annotation sang JSONB record."""
    return SemanticAnnotationRecord(
        requirement_id=annotation.requirement_id,
        required_concept_key=annotation.required_concept_key,
        decision=annotation.decision,
        provenance=annotation.provenance,
        candidate_label=annotation.candidate_label,
        role_key=annotation.role_key,
        role_label=annotation.role_label,
    )


def record_to_annotation(
    record: SemanticAnnotationRecord,
) -> SourceSemanticAnnotation:
    """Khôi phục semantic annotation từ typed record."""
    return SourceSemanticAnnotation(
        record.requirement_id,
        record.required_concept_key,
        record.decision,
        record.provenance,
        record.candidate_label,
        record.role_key,
        record.role_label,
    )
