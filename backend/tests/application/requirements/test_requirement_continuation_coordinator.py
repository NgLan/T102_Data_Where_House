"""Application tests cho Requirement continuation command."""

from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.application.requirements.input import ChooseRequirementContinuationInput
from src.application.requirements.requirement_continuation_coordinator import (
    RequirementContinuationCoordinator,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.project.entities import Project
from src.domain.project_session.entities import ProjectSession
from src.domain.project_session.enums import (
    RequirementContinuationAction,
    RequirementContinuationState,
    SessionPurpose,
)

from tests.fakes import FakeUnitOfWork


@pytest.mark.anyio
async def test_choose_continuation_persists_idempotent_action() -> None:
    project, session, dependencies = _context()
    data = ChooseRequirementContinuationInput(
        project.id, session.id, RequirementContinuationAction.CONTINUE_EDITING, 3
    )
    coordinator = RequirementContinuationCoordinator(dependencies)

    first = await coordinator.choose(data)
    second = await coordinator.choose(data)

    assert first == second == "current-state"
    assert session.requirement_continuation_state is RequirementContinuationState.CONTINUE_EDITING
    assert dependencies.unit_of_work.commit_count == 2


@pytest.mark.anyio
async def test_choose_continuation_rejects_stale_revision() -> None:
    project, session, dependencies = _context()
    coordinator = RequirementContinuationCoordinator(dependencies)

    with pytest.raises(BusinessException) as raised:
        await coordinator.choose(ChooseRequirementContinuationInput(
            project.id, session.id, RequirementContinuationAction.CONTINUE_ANALYSIS, 2
        ))

    assert raised.value.code is ErrorCode.REQUIREMENT_REVISION_CONFLICT


def _context():
    owner_id = uuid4()
    project = Project(name="Demo", requirement="Phân tích doanh thu", user_id=owner_id)
    project.requirement_revision = 3
    project.analyzed_requirement_revision = 3
    session = ProjectSession(
        project_id=project.id,
        user_id=owner_id,
        purpose=SessionPurpose.REQUIREMENT_CLARIFICATION,
        base_requirement_revision=3,
        requirement_continuation_state=RequirementContinuationState.AWAITING_DECISION,
    )
    access = SimpleNamespace(require_owner_for_update=AsyncMock(return_value=project))
    sessions = SimpleNamespace(
        get_by_id_for_update=AsyncMock(return_value=session), save=AsyncMock()
    )
    state = SimpleNamespace(read=AsyncMock(return_value="current-state"))
    dependencies = SimpleNamespace(
        access=access, sessions=sessions, state=state, unit_of_work=FakeUnitOfWork()
    )
    return project, session, dependencies
