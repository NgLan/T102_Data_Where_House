"""Render Source Coverage context mà không đưa database UUID qua LLM boundary."""

from dataclasses import asdict
from enum import Enum

from src.application.requirements.input import EvaluateSourceCoverageInput
from src.common.utils.json import safe_json_dumps
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.data_source.entities import DataSource
from src.domain.data_source.semantic_metadata import SourceSemanticAnnotation
from src.domain.data_source.value_objects import (
    ColumnMetadata,
    RelationshipMetadata,
    SchemaMetadata,
)
from src.infrastructure.agents.transport_references import (
    SourceCoverageReferenceBoundary,
    TransportReferenceMap,
)


def render_source_coverage_input(
    data: EvaluateSourceCoverageInput,
    references: SourceCoverageReferenceBoundary,
) -> tuple[str, str, str]:
    """Render requirement, analytical và source refs ổn định cho một attempt."""
    requirements = [
        {
            "requirement_ref": references.requirements.reference_for(item.id),
            "title": item.title,
            "description": item.description,
            "requirement_type": _enum_value(item.requirement_type),
            "priority": _enum_value(item.priority),
        }
        for item in data.requirements
    ]
    analytical = [_analytical(item, references) for item in data.analytical_requirements]
    sources = [_source(item, references) for item in data.data_sources]
    return tuple(safe_json_dumps(value, indent=2) for value in (requirements, analytical, sources))


def _analytical(
    item: AnalyticalRequirement,
    references: SourceCoverageReferenceBoundary,
) -> dict[str, object]:
    return {
        "analytical_requirement_ref": references.analytical_requirements.reference_for(item.id),
        "requirement_ref": references.requirements.reference_for(item.requirement_id),
        "metric": item.metric,
        "dimension": item.dimension,
        "time_granularity": item.time_granularity,
        "aggregation_method": item.aggregation_method.value if item.aggregation_method else None,
        "grain": item.grain,
    }


def _source(
    item: DataSource,
    references: SourceCoverageReferenceBoundary,
) -> dict[str, object]:
    return {
        "source_ref": references.sources.reference_for(item.id),
        "name": item.name,
        "type": item.type.value,
        "description": item.description,
        "schema_metadata": _schema(item.schema_metadata, references.requirements),
    }


def _schema(
    schema: SchemaMetadata | None,
    requirement_refs: TransportReferenceMap,
) -> dict[str, object] | None:
    if schema is None:
        return None
    tables = []
    for table in schema.tables:
        record = asdict(table)
        record["columns"] = [_column(column, requirement_refs) for column in table.columns]
        tables.append(record)
    relationships = [_relationship(item, requirement_refs) for item in schema.relationships]
    return {"tables": tables, "relationships": relationships}


def _column(
    column: ColumnMetadata,
    requirement_refs: TransportReferenceMap,
) -> dict[str, object]:
    record = asdict(column)
    record["semantic_annotations"] = _annotations(column.semantic_annotations, requirement_refs)
    return record


def _relationship(
    item: RelationshipMetadata,
    requirement_refs: TransportReferenceMap,
) -> dict[str, object]:
    record = asdict(item)
    record["semantic_annotations"] = _annotations(item.semantic_annotations, requirement_refs)
    return record


def _annotations(
    items: tuple[SourceSemanticAnnotation, ...],
    requirement_refs: TransportReferenceMap,
) -> list[dict[str, object]]:
    result = []
    for item in items:
        reference = requirement_refs.reference_for(item.requirement_id) if item.requirement_id else None
        if item.requirement_id and reference is None:
            continue
        record = asdict(item)
        record.pop("requirement_id", None)
        record["requirement_ref"] = reference
        result.append(record)
    return result


def _enum_value(value: Enum | str) -> str:
    return str(value.value) if isinstance(value, Enum) else value
