"""Persisted HITL state-machine contracts for Sandbox execution."""

from datetime import timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.application.agent_tools import (
    AgentToolIntent,
    AgentToolName,
    AgentToolPreparation,
    AgentToolRequest,
    AgentToolResult,
)
from src.application.project_sessions.session_event_factory import create_agent_call
from src.application.project_sessions.session_tool_coordinator import (
    SessionToolCoordinator,
    SessionToolDependencies,
    ToolResumeInput,
)
from src.common.utils.datetime import utc_now
from src.domain.project_session.entities import ProjectSession
from src.domain.project_session.enums import SessionEventType, SessionQuestionKind
from src.domain.sandbox.enums import SandboxEndpointRisk

from tests.fakes import FakeUnitOfWork


@pytest.mark.asyncio
async def test_mode_then_confirmation_persists_ordered_tool_execution() -> None:
    session = ProjectSession(project_id=uuid4(), user_id=uuid4())
    turn_id = uuid4()
    session.acquire_turn(turn_id, utc_now() - timedelta(minutes=1))
    events: list = []
    event_repository = AsyncMock()
    event_repository.save.side_effect = lambda event: events.append(event) or event
    tools = AsyncMock()
    request = AgentToolRequest(session.project_id, AgentToolName.EXECUTE_SANDBOX_DDL)
    prepared = AgentToolPreparation(request, True, 4, SandboxEndpointRisk.PRIVATE_NETWORK, "analytics")
    tools.prepare.return_value = prepared
    tools.execute.return_value = AgentToolResult(
        request.name, True, "Executed", executed_statements=2, succeeded_statements=2
    )
    coordinator = SessionToolCoordinator(
        SessionToolDependencies(AsyncMock(), event_repository, FakeUnitOfWork(), tools)
    )

    first = await coordinator.start(session, create_agent_call(session.id, turn_id), AgentToolIntent(request, True))
    mode_question = events[-1]
    assert first.question_kind is SessionQuestionKind.SANDBOX_MODE_SELECTION
    session.resume_turn(mode_question.id, turn_id, utc_now() - timedelta(minutes=1))
    second = await coordinator.resume(
        ToolResumeInput(session, mode_question, create_agent_call(session.id, turn_id), 0)
    )
    confirmation = events[-1]
    assert second.question_kind is SessionQuestionKind.TOOL_CONFIRMATION
    session.resume_turn(confirmation.id, turn_id, utc_now() - timedelta(minutes=1))
    await coordinator.resume(ToolResumeInput(session, confirmation, create_agent_call(session.id, turn_id), 0))

    assert [event.type for event in events] == [
        SessionEventType.QUESTION,
        SessionEventType.QUESTION,
        SessionEventType.TOOL_CALL,
        SessionEventType.TOOL_RESULT,
        SessionEventType.AGENT_RESULT,
        SessionEventType.MESSAGE,
    ]
    tools.execute.assert_awaited_once()
    assert session.active_turn_id is None
    assert session.pending_question_id is None
