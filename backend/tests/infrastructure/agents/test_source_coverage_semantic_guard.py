"""Role-aware USER semantic guard regressions."""

from uuid import UUID, uuid4

import pytest
from src.application.requirements.output import (
    GeneratedSourceCoverageAssessment,
    GeneratedSourceCoverageCandidate,
    GeneratedSourceCoverageReference,
)
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.analytical_requirement.enums import (
    SourceCandidateKind,
    SourceConfirmationQuestionType,
    SourceCoverageStatus,
)
from src.domain.data_source.entities import DataSource
from src.domain.data_source.enums import (
    ColumnDataType,
    DataSourceType,
    SourceSemanticDecision,
)
from src.domain.data_source.semantic_metadata import SourceSemanticAnnotation
from src.domain.data_source.value_objects import ColumnMetadata, SchemaMetadata, TableMetadata
from src.infrastructure.agents.source_coverage_semantic_guard import reject_repeated_confirmation


def test_guard_requires_every_role_before_mapping_counts_as_confirmed() -> None:
    requirement_id, source_id = uuid4(), uuid4()
    source = _source(source_id)
    assessment = _assessment(source_id)
    source.annotate_column(
        "visits",
        "admitted_at",
        _annotation(requirement_id, "START_TIME", "Treatment start"),
    )
    reject_repeated_confirmation((assessment,), requirement_id, {source_id: source})
    source.annotate_column(
        "visits",
        "discharged_at",
        _annotation(requirement_id, "END_TIME", "Treatment end"),
    )
    with pytest.raises(InfrastructureException):
        reject_repeated_confirmation((assessment,), requirement_id, {source_id: source})


def _assessment(source_id: UUID) -> GeneratedSourceCoverageAssessment:
    references = (
        _reference(source_id, "admitted_at", ("START_TIME", "Treatment start")),
        _reference(source_id, "discharged_at", ("END_TIME", "Treatment end")),
    )
    return GeneratedSourceCoverageAssessment(
        status=SourceCoverageStatus.NEEDS_SOURCE_CONFIRMATION,
        required_concept_key="TREATMENT_DURATION",
        title="Confirm duration",
        explanation="Both events are needed.",
        question="Use these events?",
        question_type=SourceConfirmationQuestionType.FIELD_SET_CONFIRMATION,
        candidates=(GeneratedSourceCoverageCandidate("Admission to discharge", references),),
    )


def _reference(
    source_id: UUID,
    column: str,
    role: tuple[str, str],
) -> GeneratedSourceCoverageReference:
    return GeneratedSourceCoverageReference(
        SourceCandidateKind.COLUMN,
        source_id,
        role[0],
        role[1],
        "visits",
        column,
    )


def _annotation(
    requirement_id: UUID,
    role_key: str,
    role_label: str,
) -> SourceSemanticAnnotation:
    return SourceSemanticAnnotation(
        requirement_id,
        "TREATMENT_DURATION",
        SourceSemanticDecision.CONFIRMED,
        candidate_label="Admission to discharge",
        role_key=role_key,
        role_label=role_label,
    )


def _source(source_id: UUID) -> DataSource:
    columns = (
        ColumnMetadata("admitted_at", ColumnDataType.DATETIME),
        ColumnMetadata("discharged_at", ColumnDataType.DATETIME),
    )
    return DataSource(
        id=source_id,
        project_id=uuid4(),
        name="visits.csv",
        location="visits.csv",
        type=DataSourceType.CSV,
        schema_metadata=SchemaMetadata((TableMetadata("visits", columns, 2),)),
    )
