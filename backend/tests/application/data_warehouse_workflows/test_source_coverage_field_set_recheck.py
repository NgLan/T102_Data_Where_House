"""Grouped Source Coverage mapping materialization regressions."""

from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest
from src.application.data_warehouse_workflows.input import RecheckSourceCoverageInput
from src.application.data_warehouse_workflows.source_coverage_recheck import SourceCoverageRechecker
from src.application.data_warehouse_workflows.source_coverage_recheck_rules import (
    resolution_candidates,
)
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.analytical_requirement.enums import (
    SourceCandidateKind,
    SourceConfirmationQuestionType,
    SourceConfirmationStatus,
    SourceCoverageStatus,
)
from src.domain.analytical_requirement.source_coverage import SourceCoverageAssessment
from src.domain.analytical_requirement.source_coverage_candidate import (
    SourceCoverageCandidate,
    SourceCoverageReference,
)
from src.domain.data_source.entities import DataSource
from src.domain.data_source.enums import ColumnDataType, DataSourceType
from src.domain.data_source.value_objects import ColumnMetadata, SchemaMetadata, TableMetadata
from src.domain.project.entities import Project


@pytest.mark.asyncio
async def test_confirmed_field_set_materializes_every_reference_with_its_role() -> None:
    project_id, batch_id, source_id = uuid4(), uuid4(), uuid4()
    candidate = SourceCoverageCandidate(
        uuid4(),
        "Admission to discharge",
        (
            _reference(source_id, "admitted_at", ("START_TIME", "Treatment start")),
            _reference(source_id, "discharged_at", ("END_TIME", "Treatment end")),
        ),
    )
    assessment = SourceCoverageAssessment(
        id=uuid4(),
        batch_id=batch_id,
        evaluated_source_revision=4,
        status=SourceCoverageStatus.NEEDS_SOURCE_CONFIRMATION,
        required_concept_key="TREATMENT_DURATION",
        title="Confirm treatment duration",
        explanation="Both events are required.",
        question="Use these events?",
        question_type=SourceConfirmationQuestionType.FIELD_SET_CONFIRMATION,
        confirmation_status=SourceConfirmationStatus.CONFIRMED,
        selected_candidate_id=candidate.id,
        resolution_revision=1,
        candidates=(candidate,),
    )
    analytical = AnalyticalRequirement(requirement_id=uuid4(), source_coverage=(assessment,))
    source, project = _source(project_id, source_id), _project(project_id)
    rechecker = SourceCoverageRechecker(
        SimpleNamespace(save=AsyncMock()),
        SimpleNamespace(list_by_project=AsyncMock(return_value=[analytical]), save=AsyncMock()),
        SimpleNamespace(list_by_project=AsyncMock(return_value=[source]), save=AsyncMock()),
        AsyncMock(),
        SimpleNamespace(require_owner_for_update=AsyncMock(return_value=project)),
    )
    await rechecker.prepare(RecheckSourceCoverageInput(project_id, batch_id, 4))
    annotations = [column.semantic_annotations[0] for column in source.schema_metadata.tables[0].columns]
    assert [item.role_key for item in annotations] == ["START_TIME", "END_TIME"]
    assert all(item.candidate_label == "Admission to discharge" for item in annotations)


def test_rejected_selection_returns_every_candidate_for_materialization() -> None:
    source_id = uuid4()
    candidates = (
        SourceCoverageCandidate(uuid4(), "Patient record", (_plain_reference(source_id, "patient_id"),)),
        SourceCoverageCandidate(uuid4(), "Medical record", (_plain_reference(source_id, "record_id"),)),
    )
    assessment = SourceCoverageAssessment(
        id=uuid4(),
        batch_id=uuid4(),
        evaluated_source_revision=1,
        status=SourceCoverageStatus.NEEDS_SOURCE_CONFIRMATION,
        required_concept_key="PATIENT_IDENTITY",
        title="Choose identity",
        explanation="The identifier affects unique counts.",
        question="Which field?",
        question_type=SourceConfirmationQuestionType.SINGLE_FIELD_SELECTION,
        confirmation_status=SourceConfirmationStatus.REJECTED,
        candidates=candidates,
    )
    assert resolution_candidates(assessment) == candidates


def _reference(
    source_id: UUID,
    column: str,
    role: tuple[str, str],
) -> SourceCoverageReference:
    return SourceCoverageReference(
        SourceCandidateKind.COLUMN,
        source_id,
        role[0],
        role[1],
        table_name="visits",
        column_name=column,
    )


def _plain_reference(source_id: UUID, column: str) -> SourceCoverageReference:
    return SourceCoverageReference(
        SourceCandidateKind.COLUMN,
        source_id,
        table_name="visits",
        column_name=column,
    )


def _source(project_id: UUID, source_id: UUID) -> DataSource:
    columns = (
        ColumnMetadata("admitted_at", ColumnDataType.DATETIME),
        ColumnMetadata("discharged_at", ColumnDataType.DATETIME),
    )
    schema = SchemaMetadata((TableMetadata("visits", columns, 2),))
    return DataSource(
        id=source_id,
        project_id=project_id,
        name="visits.csv",
        location="visits.csv",
        type=DataSourceType.CSV,
        schema_metadata=schema,
    )


def _project(project_id: UUID) -> Project:
    project = Project(
        id=project_id,
        name="Project",
        user_id=uuid4(),
        requirement="treatment duration",
    )
    project.analyzed_requirement_revision = project.derived_analytical_requirement_revision = 1
    project.covered_analytical_requirement_revision = 1
    project.source_revision = project.analyzed_source_revision = 4
    return project
