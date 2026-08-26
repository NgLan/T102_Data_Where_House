"""Item-scoped Source Confirmation workflow regressions."""

from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.application.data_warehouse_workflows.data_warehouse_workflow_service import (
    DataWarehouseWorkflowService,
)
from src.application.data_warehouse_workflows.input import ResolveSourceCoverageInput
from src.application.data_warehouse_workflows.output import InputReadinessStatus
from src.application.data_warehouse_workflows.source_coverage_resolution import (
    SourceCoverageResolver,
)
from src.common.exceptions.business import BusinessException
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.analytical_requirement.enums import (
    SourceCandidateKind,
    SourceConfirmationStatus,
    SourceCoverageResolutionAction,
    SourceCoverageStatus,
)
from src.domain.analytical_requirement.source_coverage import (
    SourceCoverageAssessment,
    SourceCoverageCandidate,
)
from src.domain.project.entities import Project


@pytest.mark.asyncio
async def test_resolution_does_not_invoke_source_coverage() -> None:
    service = object.__new__(DataWarehouseWorkflowService)
    service._coverage_resolver = AsyncMock()  # noqa: SLF001
    service._analysis = AsyncMock()  # noqa: SLF001
    service._access = AsyncMock()  # noqa: SLF001
    service._reader = AsyncMock()  # noqa: SLF001
    service._reader.calculate_analysis_status.return_value = "status"  # noqa: SLF001
    data = _input(uuid4(), uuid4(), uuid4())
    assert await service.resolve_source_coverage(data) == "status"
    service._coverage_resolver.resolve.assert_awaited_once_with(data)  # noqa: SLF001
    service._analysis.run_source_coverage.assert_not_awaited()  # noqa: SLF001


@pytest.mark.asyncio
async def test_three_items_resolve_independently_without_source_revision_change() -> None:
    project_id, batch_id = uuid4(), uuid4()
    project = _current_project(project_id)
    assessments = tuple(_assessment(batch_id, project.source_revision) for _ in range(3))
    analytical = AnalyticalRequirement(requirement_id=uuid4(), source_coverage=assessments)
    repository = SimpleNamespace(
        list_by_project=AsyncMock(return_value=[analytical]),
        save=AsyncMock(),
    )
    unit_of_work = AsyncMock()
    access = SimpleNamespace(require_owner_for_update=AsyncMock(return_value=project))
    resolver = SourceCoverageResolver(repository, unit_of_work, access)
    await resolver.resolve(_confirm_input(project_id, assessments[0], batch_id))
    await resolver.resolve(_confirm_input(project_id, assessments[1], batch_id))
    await resolver.resolve(_input(project_id, assessments[2].id, batch_id))
    assert [item.confirmation_status for item in analytical.source_coverage] == [
        SourceConfirmationStatus.CONFIRMED,
        SourceConfirmationStatus.CONFIRMED,
        SourceConfirmationStatus.REJECTED,
    ]
    assert project.source_revision == 4
    with pytest.raises(BusinessException):
        await resolver.resolve(_confirm_input(project_id, assessments[0], batch_id))
    assert unit_of_work.commit.await_count == 3


@pytest.mark.asyncio
@pytest.mark.parametrize("readiness", [
    InputReadinessStatus.SOURCE_CONFIRMATION_REQUIRED,
    InputReadinessStatus.SOURCE_DATA_REQUIRED,
    InputReadinessStatus.REQUIREMENT_CLARIFICATION_REQUIRED,
])
async def test_every_blocking_readiness_stops_design(readiness: InputReadinessStatus) -> None:
    service = object.__new__(DataWarehouseWorkflowService)
    service._reader = AsyncMock()  # noqa: SLF001
    service._reader.calculate_analysis_status.return_value = SimpleNamespace(
        readiness_status=readiness
    )
    with pytest.raises(BusinessException):
        await service._ensure_ready_for_design(SimpleNamespace(id=uuid4()))  # noqa: SLF001


def _assessment(batch_id, revision) -> SourceCoverageAssessment:
    candidate = SourceCoverageCandidate(
        uuid4(), SourceCandidateKind.COLUMN, uuid4(), "visits", "record_no"
    )
    return SourceCoverageAssessment(
        id=uuid4(), batch_id=batch_id, evaluated_source_revision=revision,
        status=SourceCoverageStatus.NEEDS_SOURCE_CONFIRMATION,
        required_concept_key=f"CONCEPT_{uuid4().hex}", title="Choose a field",
        explanation="A field must be confirmed.", question="Which field?",
        candidates=(candidate,),
    )


def _input(project_id, assessment_id, batch_id) -> ResolveSourceCoverageInput:
    return ResolveSourceCoverageInput(
        project_id, assessment_id, batch_id, 4, 0,
        SourceCoverageResolutionAction.REJECT_ALL_CANDIDATES,
    )


def _confirm_input(project_id, assessment, batch_id) -> ResolveSourceCoverageInput:
    return ResolveSourceCoverageInput(
        project_id, assessment.id, batch_id, 4, 0,
        SourceCoverageResolutionAction.CONFIRM_CANDIDATE,
        assessment.candidates[0].id,
    )


def _current_project(project_id):
    project = Project(id=project_id, name="Project", user_id=uuid4(), requirement="count patients")
    project.analyzed_requirement_revision = 1
    project.derived_analytical_requirement_revision = 1
    project.covered_analytical_requirement_revision = 1
    project.source_revision = project.analyzed_source_revision = 4
    return project
