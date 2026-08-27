"""Completed Source Confirmation batch recheck regressions."""

from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.application.data_warehouse_workflows.data_warehouse_workflow_service import DataWarehouseWorkflowService
from src.application.data_warehouse_workflows.input import RecheckSourceCoverageInput
from src.application.data_warehouse_workflows.source_coverage_recheck import SourceCoverageRechecker
from src.common.exceptions.business import BusinessException
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
from src.domain.data_source.enums import ColumnDataType, DataSourceType, SourceSemanticDecision
from src.domain.data_source.value_objects import ColumnMetadata, SchemaMetadata, TableMetadata
from src.domain.project.entities import Project


@pytest.mark.asyncio
async def test_recheck_materializes_all_answers_and_increments_once() -> None:
    project_id, batch_id, source_id = uuid4(), uuid4(), uuid4()
    project = _current_project(project_id)
    assessments = tuple(
        _resolved_assessment(batch_id, source_id, name, decision)
        for name, decision in (("patient_id", "CONFIRMED"), ("admitted_at", "CONFIRMED"), ("status", "REJECTED"))
    )
    analytical = AnalyticalRequirement(requirement_id=uuid4(), source_coverage=assessments)
    source = _source(project_id, source_id)
    rechecker, unit, sources = _rechecker(project, analytical, source)
    await rechecker.prepare(RecheckSourceCoverageInput(project_id, batch_id, 4))
    assert project.source_revision == 5
    annotations = [item.semantic_annotations[0] for item in source.schema_metadata.tables[0].columns]
    assert [item.decision for item in annotations] == [
        SourceSemanticDecision.CONFIRMED,
        SourceSemanticDecision.CONFIRMED,
        SourceSemanticDecision.REJECTED,
    ]
    assert all(item.applied_source_revision == 5 for item in analytical.source_coverage)
    await rechecker.prepare(RecheckSourceCoverageInput(project_id, batch_id, 5))
    assert project.source_revision == 5
    assert sources.save.await_count == 1
    unit.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_recheck_refuses_pending_item() -> None:
    project_id, batch_id, source_id = uuid4(), uuid4(), uuid4()
    project = _current_project(project_id)
    pending = _resolved_assessment(batch_id, source_id, "patient_id", "CONFIRMED")
    pending = SourceCoverageAssessment(
        **{
            **pending.__dict__,
            "confirmation_status": SourceConfirmationStatus.PENDING,
            "selected_candidate_id": None,
        }
    )
    analytical = AnalyticalRequirement(requirement_id=uuid4(), source_coverage=(pending,))
    rechecker, _, _ = _rechecker(project, analytical, _source(project_id, source_id))
    with pytest.raises(BusinessException):
        await rechecker.prepare(RecheckSourceCoverageInput(project_id, batch_id, 4))


@pytest.mark.asyncio
async def test_service_recheck_runs_only_source_coverage() -> None:
    service = object.__new__(DataWarehouseWorkflowService)
    service._coverage_rechecker = AsyncMock()  # noqa: SLF001
    service._analysis = AsyncMock()  # noqa: SLF001
    service._reader = AsyncMock()  # noqa: SLF001
    service._reader.calculate_analysis_status.return_value = "status"  # noqa: SLF001
    data = RecheckSourceCoverageInput(uuid4(), uuid4(), 4)
    assert await service.recheck_source_coverage(data) == "status"
    service._analysis.run_source_coverage.assert_awaited_once_with(data.project_id)  # noqa: SLF001
    service._analysis.run.assert_not_called()  # noqa: SLF001


def _resolved_assessment(batch_id, source_id, column, decision):
    candidate = SourceCoverageCandidate(
        uuid4(),
        column,
        (
            SourceCoverageReference(
                SourceCandidateKind.COLUMN,
                source_id,
                table_name="visits",
                column_name=column,
            ),
        ),
    )
    status = SourceConfirmationStatus(decision)
    return SourceCoverageAssessment(
        id=uuid4(),
        batch_id=batch_id,
        evaluated_source_revision=4,
        status=SourceCoverageStatus.NEEDS_SOURCE_CONFIRMATION,
        required_concept_key=column.upper(),
        title=column,
        explanation="Choose.",
        question="Use this field?",
        question_type=SourceConfirmationQuestionType.SINGLE_CANDIDATE_CONFIRMATION,
        confirmation_status=status,
        selected_candidate_id=candidate.id if status is SourceConfirmationStatus.CONFIRMED else None,
        resolution_revision=1,
        candidates=(candidate,),
    )


def _source(project_id, source_id):
    columns = tuple(ColumnMetadata(name, ColumnDataType.TEXT) for name in ("patient_id", "admitted_at", "status"))
    return DataSource(
        id=source_id,
        project_id=project_id,
        name="visits.csv",
        location="visits.csv",
        type=DataSourceType.CSV,
        schema_metadata=SchemaMetadata((TableMetadata("visits", columns, 3),)),
    )


def _rechecker(project, analytical, source):
    unit = AsyncMock()
    sources = SimpleNamespace(list_by_project=AsyncMock(return_value=[source]), save=AsyncMock())
    rechecker = SourceCoverageRechecker(
        SimpleNamespace(save=AsyncMock()),
        SimpleNamespace(list_by_project=AsyncMock(return_value=[analytical]), save=AsyncMock()),
        sources,
        unit,
        SimpleNamespace(require_owner_for_update=AsyncMock(return_value=project)),
    )
    return rechecker, unit, sources


def _current_project(project_id):
    project = Project(id=project_id, name="Project", user_id=uuid4(), requirement="count patients")
    project.analyzed_requirement_revision = 1
    project.derived_analytical_requirement_revision = 1
    project.covered_analytical_requirement_revision = 1
    project.source_revision = project.analyzed_source_revision = 4
    return project
