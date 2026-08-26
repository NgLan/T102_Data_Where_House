from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from src.application.data_warehouse_workflows.output import AgentTurnKind, AgentTurnOutput
from src.application.project_sessions.conversation_context import (
    ConversationInputKind,
    ConversationMemory,
)
from src.application.project_sessions.input import (
    AnswerClarificationInput,
    GetPendingClarificationInput,
)
from src.application.project_sessions.session_clarification_coordinator import (
    ClarificationDependencies,
    SessionClarificationCoordinator,
)
from src.application.project_sessions.session_event_factory import (
    QuestionEventInput,
    create_question,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.project_session.entities import ProjectSession
from src.domain.project_session.enums import SessionEventType


def _coordinator(result: AgentTurnOutput):
    session = ProjectSession(project_id=uuid4(), user_id=uuid4())
    turn_id = uuid4()
    question = create_question(
        QuestionEventInput(
            session.id,
            turn_id,
            "Mức thời gian nào?",
            ("Theo ngày", "Theo tháng", "Theo quý"),
            True,
        )
    )
    session.pending_question_id = question.id
    sessions = AsyncMock()
    events = AsyncMock()
    events.get_by_id.return_value = question
    events.list_by_session.return_value = [question]
    workflow = AsyncMock()
    workflow.create_agent_turn.return_value = result
    unit_of_work = AsyncMock()
    access = AsyncMock()
    access.require.return_value = session
    context = AsyncMock()
    context.build_memory.return_value = ConversationMemory(
        None, (), "Theo tháng", ConversationInputKind.CLARIFICATION_ANSWER
    )
    coordinator = SessionClarificationCoordinator(
        ClarificationDependencies(
            sessions, events, workflow, unit_of_work, access, context
        )
    )
    return coordinator, session, question, events, workflow


def _proposal() -> AgentTurnOutput:
    proposal = MagicMock()
    proposal.summary.id = uuid4()
    return AgentTurnOutput(AgentTurnKind.PROPOSAL, proposal=proposal)


@pytest.mark.asyncio
async def test_predefined_option_resumes_waiting_turn() -> None:
    coordinator, session, question, events, workflow = _coordinator(_proposal())

    output = await coordinator.answer(AnswerClarificationInput(session.id, question.id, option_index=1))

    assert output.kind is AgentTurnKind.PROPOSAL
    assert session.pending_question_id is None
    assert session.active_turn_id is None
    assert workflow.create_agent_turn.call_args.args[0].instruction == "Theo tháng"
    assert [call.args[0].type for call in events.save.await_args_list] == [
        SessionEventType.ANSWER,
        SessionEventType.AGENT_CALL,
        SessionEventType.AGENT_RESULT,
        SessionEventType.MESSAGE,
    ]


@pytest.mark.asyncio
async def test_custom_answer_can_pause_at_next_question() -> None:
    next_result = AgentTurnOutput(
        AgentTurnKind.CLARIFICATION,
        question="Aggregation nào?",
        options=("SUM", "AVG"),
        allow_custom_answer=True,
    )
    coordinator, session, question, events, workflow = _coordinator(next_result)

    output = await coordinator.answer(AnswerClarificationInput(session.id, question.id, custom_answer="Theo tuần"))

    assert output.kind is AgentTurnKind.CLARIFICATION
    assert output.question_id != question.id
    assert session.pending_question_id == output.question_id
    assert workflow.create_agent_turn.call_args.args[0].instruction == "Theo tuần"
    assert [call.args[0].type for call in events.save.await_args_list] == [
        SessionEventType.ANSWER,
        SessionEventType.AGENT_CALL,
        SessionEventType.QUESTION,
    ]


@pytest.mark.asyncio
async def test_duplicate_answer_does_not_run_workflow_twice() -> None:
    coordinator, session, question, _, workflow = _coordinator(_proposal())
    data = AnswerClarificationInput(session.id, question.id, option_index=0)

    await coordinator.answer(data)
    with pytest.raises(BusinessException) as raised:
        await coordinator.answer(data)

    assert raised.value.code is ErrorCode.SESSION_CLARIFICATION_STALE
    assert workflow.create_agent_turn.await_count == 1


@pytest.mark.asyncio
async def test_answer_for_old_question_is_rejected() -> None:
    coordinator, session, question, _, workflow = _coordinator(_proposal())
    session.pending_question_id = uuid4()

    with pytest.raises(BusinessException) as raised:
        await coordinator.answer(AnswerClarificationInput(session.id, question.id, option_index=0))

    assert raised.value.code is ErrorCode.SESSION_CLARIFICATION_STALE
    workflow.create_agent_turn.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_pending_returns_structured_question() -> None:
    coordinator, session, question, _, _ = _coordinator(_proposal())

    pending = await coordinator.get_pending(GetPendingClarificationInput(session.id))

    assert pending is not None
    assert pending.question_id == question.id
    assert pending.options == ("Theo ngày", "Theo tháng", "Theo quý")
