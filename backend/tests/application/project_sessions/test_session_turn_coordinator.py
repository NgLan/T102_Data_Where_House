from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from src.application.data_warehouse_workflows.design_runner import WorkflowDesignRunner
from src.application.data_warehouse_workflows.input import (
    ConversationDesignInput,
    CreateAgentTurnInput,
    RevisionDesignInput,
)
from src.application.data_warehouse_workflows.output import (
    AgentTurnKind,
    AgentTurnOutput,
    ConversationDesignResult,
)
from src.application.project_sessions.conversation_context import (
    ConversationInputKind,
    ConversationMemory,
)
from src.application.project_sessions.input import SendSessionMessageInput
from src.application.project_sessions.session_turn_coordinator import (
    SessionTurnCoordinator,
    SessionTurnDependencies,
)
from src.domain.project_session.entities import ProjectSession


@pytest.mark.asyncio
async def test_workflow_design_runner_converse_delegates_to_agent() -> None:
    mock_agent = AsyncMock()
    mock_validator = MagicMock()
    expected_result = ConversationDesignResult(
        AgentTurnKind.CLARIFICATION,
        question="Which columns?",
        options=("Orders", "Order lines"),
        allow_custom_answer=True,
    )
    mock_agent.converse.return_value = expected_result

    runner = WorkflowDesignRunner(mock_agent, mock_validator)
    data = ConversationDesignInput(
        RevisionDesignInput((), (), (), "Table a {}", "add index"),
        ConversationMemory(
            None, (), "add index", ConversationInputKind.USER_MESSAGE
        ),
    )
    result = await runner.converse(data)

    assert result == expected_result
    mock_agent.converse.assert_awaited_once_with(data)


@pytest.mark.asyncio
async def test_session_turn_coordinator_executes_turn_and_releases_lock() -> None:
    session_id = uuid4()
    project_id = uuid4()
    user_id = uuid4()
    session = ProjectSession(id=session_id, project_id=project_id, user_id=user_id)

    mock_sessions = AsyncMock()
    mock_events = AsyncMock()
    mock_events.list_by_session.return_value = []
    mock_workflow = AsyncMock()
    mock_workflow.create_agent_turn.return_value = AgentTurnOutput(
        AgentTurnKind.CLARIFICATION,
        question="Please specify currency.",
        options=("USD", "Source currency"),
        allow_custom_answer=True,
    )
    mock_uow = AsyncMock()
    mock_access = AsyncMock()
    mock_access.require.return_value = session
    mock_context = AsyncMock()
    mock_context.build_memory.return_value = ConversationMemory(
        None, (), "Design a payments warehouse", ConversationInputKind.USER_MESSAGE
    )

    coordinator = SessionTurnCoordinator(
        SessionTurnDependencies(
            sessions=mock_sessions,
            events=mock_events,
            workflow=mock_workflow,
            unit_of_work=mock_uow,
            access=mock_access,
            context=mock_context,
        )
    )

    output = await coordinator.send(SendSessionMessageInput(session_id, "Design a payments warehouse"))

    assert output.session_id == session_id
    assert output.kind == "clarification"
    assert output.question == "Please specify currency."
    assert session.active_turn_id is None
    mock_workflow.create_agent_turn.assert_awaited_once()
    called_input: CreateAgentTurnInput = mock_workflow.create_agent_turn.call_args[0][0]
    assert called_input.turn_id is not None
    assert called_input.instruction == "Design a payments warehouse"


@pytest.mark.asyncio
async def test_session_turn_no_change_does_not_create_proposal_reference() -> None:
    session = ProjectSession(project_id=uuid4(), user_id=uuid4())
    mock_sessions = AsyncMock()
    mock_events = AsyncMock()
    mock_events.list_by_session.return_value = []
    mock_workflow = AsyncMock()
    mock_workflow.create_agent_turn.return_value = AgentTurnOutput(
        AgentTurnKind.NO_CHANGE,
        summary="Mô hình hiện tại đã đáp ứng yêu cầu.",
    )
    mock_access = AsyncMock()
    mock_access.require.return_value = session
    mock_context = AsyncMock()
    mock_context.build_memory.return_value = ConversationMemory(
        None, (), "No change", ConversationInputKind.USER_MESSAGE
    )
    coordinator = SessionTurnCoordinator(
        SessionTurnDependencies(
            mock_sessions,
            mock_events,
            mock_workflow,
            AsyncMock(),
            mock_access,
            mock_context,
        )
    )

    output = await coordinator.send(SendSessionMessageInput(session.id, "Kiểm tra mô hình hiện tại"))

    assert output.kind is AgentTurnKind.NO_CHANGE
    assert output.proposal_change_id is None
    saved_result = next(
        call.args[0]
        for call in mock_events.save.await_args_list
        if call.args[0].type.value == "AGENT_RESULT"
    )
    assert saved_result.metadata.output_data is None
