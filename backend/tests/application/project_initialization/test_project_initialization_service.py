"""Behavior tests cho entry point Project Initialization."""

from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.application.data_warehouse_workflows.output import InputReadinessStatus
from src.application.project_initialization import (
    ProjectInitializationInput,
    ProjectInitializationStatus,
)
from src.application.project_initialization.project_initialization_service import (
    ProjectInitializationService,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.project_session.enums import (
    RequirementClarificationStatus,
    RequirementContinuationState,
)


@pytest.mark.asyncio
async def test_current_structured_requirements_skip_requirement_agent() -> None:
    requirements = AsyncMock()
    data_warehouse = AsyncMock()
    project_id, model_id = uuid4(), uuid4()
    requirements.get_clarification.return_value = _state(RequirementClarificationStatus.READY, False)
    data_warehouse.synchronize_data_model.return_value = SimpleNamespace(id=model_id)
    data_warehouse.reanalyze.return_value = _analysis(InputReadinessStatus.READY_FOR_DESIGN)
    result = await ProjectInitializationService(requirements, data_warehouse).run(
        ProjectInitializationInput(project_id)
    )
    requirements.analyze_clarification.assert_not_awaited()
    data_warehouse.synchronize_data_model.assert_awaited_once()
    assert result.status is ProjectInitializationStatus.COMPLETED
    assert result.data_model_id == model_id


@pytest.mark.asyncio
async def test_ambiguous_requirement_pauses_before_source_analysis() -> None:
    requirements = AsyncMock()
    data_warehouse = AsyncMock()
    project_id, session_id = uuid4(), uuid4()
    requirements.get_clarification.return_value = _state(RequirementClarificationStatus.IDLE, True)
    requirements.analyze_clarification.return_value = _state(
        RequirementClarificationStatus.NEEDS_CLARIFICATION,
        False,
        session_id,
    )
    result = await ProjectInitializationService(requirements, data_warehouse).run(
        ProjectInitializationInput(project_id)
    )
    data_warehouse.synchronize_data_model.assert_not_awaited()
    assert result.status is ProjectInitializationStatus.PAUSED
    assert result.session_id == session_id


@pytest.mark.asyncio
async def test_downstream_semantic_gap_returns_to_requirement_clarification() -> None:
    requirements, data_warehouse = AsyncMock(), AsyncMock()
    project_id, session_id = uuid4(), uuid4()
    current = _state(RequirementClarificationStatus.READY, False)
    requirements.get_clarification.return_value = current
    requirements.analyze_clarification.return_value = _state(
        RequirementClarificationStatus.NEEDS_CLARIFICATION, False, session_id
    )
    data_warehouse.reanalyze.side_effect = BusinessException(
        ErrorCode.REQUIREMENT_SEMANTIC_CLARIFICATION_REQUIRED,
        "Counting unit is unresolved.",
    )

    result = await ProjectInitializationService(requirements, data_warehouse).run(
        ProjectInitializationInput(project_id)
    )

    requirements.analyze_clarification.assert_awaited_once()
    assert result.status is ProjectInitializationStatus.PAUSED
    assert result.session_id == session_id


@pytest.mark.asyncio
async def test_source_blocker_is_returned_as_normal_pause() -> None:
    requirements, data_warehouse = AsyncMock(), AsyncMock()
    project_id = uuid4()
    requirements.get_clarification.return_value = _state(RequirementClarificationStatus.READY, False)
    data_warehouse.reanalyze.return_value = _analysis(
        InputReadinessStatus.SOURCE_DATA_REQUIRED, (SimpleNamespace(id=uuid4()),)
    )

    result = await ProjectInitializationService(requirements, data_warehouse).run(
        ProjectInitializationInput(project_id)
    )

    assert result.status is ProjectInitializationStatus.PAUSED
    assert result.readiness_status is InputReadinessStatus.SOURCE_DATA_REQUIRED
    data_warehouse.synchronize_data_model.assert_not_awaited()
    requirements.analyze_clarification.assert_not_awaited()


@pytest.mark.asyncio
async def test_awaiting_continuation_pauses_before_source_analysis() -> None:
    requirements, data_warehouse = AsyncMock(), AsyncMock()
    session_id = uuid4()
    requirements.get_clarification.return_value = _state(
        RequirementClarificationStatus.READY,
        False,
        session_id,
        RequirementContinuationState.AWAITING_DECISION,
    )

    result = await ProjectInitializationService(requirements, data_warehouse).run(
        ProjectInitializationInput(uuid4())
    )

    assert result.status is ProjectInitializationStatus.PAUSED
    data_warehouse.synchronize_data_model.assert_not_awaited()


def _state(
    status: RequirementClarificationStatus,
    outdated: bool,
    session_id=None,
    continuation_state: RequirementContinuationState = RequirementContinuationState.NOT_REQUIRED,
):
    session = SimpleNamespace(id=session_id) if session_id else None
    return SimpleNamespace(
        status=status,
        is_outdated=outdated,
        requirement_revision=3,
        session=session,
        continuation_state=continuation_state,
    )


def _analysis(readiness_status: InputReadinessStatus, source_coverage_batch=None):
    return SimpleNamespace(
        readiness_status=readiness_status,
        source_coverage_batch=source_coverage_batch,
    )
