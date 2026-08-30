"""Canonical-reference validation for semantic analysis output."""

from dataclasses import dataclass

from src.application.data_model_analysis.models import (
    AnalysisSemanticInput,
    AnalysisSemanticOutput,
    EvidenceLevel,
    SemanticObservation,
)
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class _GroundingCatalog:
    tables: dict[str, set[str]]
    requirements: set[EntityID]
    sources: set[EntityID]


def validate_semantic_output(data: AnalysisSemanticInput, output: AnalysisSemanticOutput) -> AnalysisSemanticOutput:
    catalog = _GroundingCatalog(
        {table.name: {column.name for column in table.columns} for table in data.structure.tables},
        set(data.requirement_ids),
        set(data.source_ids),
    )
    observations = tuple(_validate_observation(item, catalog) for item in output.observations)
    return AnalysisSemanticOutput(observations, output.uncertainties)


def _validate_observation(item: SemanticObservation, catalog: _GroundingCatalog) -> SemanticObservation:
    if item.table_name and item.table_name not in catalog.tables:
        raise ValueError("Semantic output references an unknown table.")
    if item.column_name and (not item.table_name or item.column_name not in catalog.tables[item.table_name]):
        raise ValueError("Semantic output references an unknown column.")
    if item.requirement_id and item.requirement_id not in catalog.requirements:
        raise ValueError("Semantic output references an unknown requirement.")
    if item.source_id and item.source_id not in catalog.sources:
        raise ValueError("Semantic output references an unknown source.")
    evidence = item.evidence
    has_reference = any((item.table_name, item.column_name, item.requirement_id, item.source_id))
    if evidence in {EvidenceLevel.CONFIRMED, EvidenceLevel.INFERRED} and not has_reference:
        evidence = EvidenceLevel.UNKNOWN
    return SemanticObservation(
        item.explanation,
        evidence,
        item.table_name,
        item.column_name,
        item.requirement_id,
        item.source_id,
    )
