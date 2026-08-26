from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.application.project_sessions.conversation_canonical_index import (
    ConversationCanonicalIndexReader,
)
from src.application.project_sessions.conversation_context import (
    ConversationInputKind,
    group_conversation_turns,
)
from src.application.project_sessions.conversation_context_policy import (
    ConversationContextPolicy,
    ConversationMemoryInput,
)
from src.application.project_sessions.conversation_summary_compactor import (
    ConversationSummaryCompactor,
    SummaryCompactorDependencies,
)
from src.domain.project_session.conversation_summary import ConversationSummary
from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.project_session.enums import SessionEventRole, SessionEventType


def _events(session_id, count: int, shared_turn_id=None) -> list[SessionEvent]:
    events = []
    for index in range(count):
        turn_id = shared_turn_id or uuid4()
        events.extend(
            (
                SessionEvent(
                    session_id=session_id,
                    turn_id=turn_id,
                    role=SessionEventRole.USER,
                    type=SessionEventType.MESSAGE,
                    content=f"user-{index}",
                ),
                SessionEvent(
                    session_id=session_id,
                    turn_id=turn_id,
                    role=SessionEventRole.AGENT,
                    type=SessionEventType.MESSAGE,
                    content=f"agent-{index}",
                ),
            )
        )
    return events


def test_grouping_uses_event_order_not_turn_id_and_ignores_incomplete_pair() -> None:
    session_id, turn_id = uuid4(), uuid4()
    events = _events(session_id, 2, turn_id)
    events.append(
        SessionEvent(
            session_id=session_id,
            turn_id=turn_id,
            role=SessionEventRole.USER,
            type=SessionEventType.MESSAGE,
            content="incomplete",
        )
    )

    turns = group_conversation_turns(events)

    assert len(turns) == 2
    assert turns[0].user_content == "user-0"
    assert turns[1].agent_content == "agent-1"


@pytest.mark.parametrize("completed_turns", (0, 3, 6, 9))
@pytest.mark.asyncio
async def test_below_checkpoint_does_not_call_summary_agent(
    completed_turns: int,
) -> None:
    compactor, session, agent = _compactor(completed_turns)

    memory = await compactor.build_memory(
        ConversationMemoryInput(
            session.id,
            session.project_id,
            "current",
            ConversationInputKind.USER_MESSAGE,
        )
    )

    agent.summarize.assert_not_awaited()
    assert len(memory.recent_turns) == min(completed_turns, 6)


@pytest.mark.asyncio
async def test_tenth_completed_turn_compacts_four_and_keeps_six() -> None:
    compactor, session, agent = _compactor(10)

    changed = await compactor.compact_if_needed(session.id, session.project_id)

    assert changed is True
    summary_input = agent.summarize.await_args.args[0]
    assert len(summary_input.turns) == 4
    assert session.summarized_through_event_id == summary_input.turns[-1].agent_event_id


@pytest.mark.asyncio
async def test_stale_checkpoint_result_does_not_overwrite_winner() -> None:
    compactor, snapshot, _ = _compactor(10)
    winner = ProjectSession(
        id=snapshot.id,
        project_id=snapshot.project_id,
        user_id=snapshot.user_id,
        summarized_through_event_id=uuid4(),
    )
    dependencies = compactor._dependencies
    dependencies.sessions.get_by_id_for_update.return_value = winner

    changed = await compactor.compact_if_needed(snapshot.id, snapshot.project_id)

    assert changed is False
    dependencies.sessions.save.assert_not_awaited()


def _compactor(completed_turns: int):
    session = ProjectSession(project_id=uuid4(), user_id=uuid4())
    sessions, events, agent = AsyncMock(), AsyncMock(), AsyncMock()
    sessions.get_by_id.return_value = session
    sessions.get_by_id_for_update.return_value = session
    events.list_conversation_events.return_value = _events(session.id, completed_turns)
    agent.summarize.return_value = ConversationSummary()
    canonical = AsyncMock(spec=ConversationCanonicalIndexReader)
    canonical.read.return_value = ()
    dependencies = SummaryCompactorDependencies(
        sessions,
        events,
        agent,
        canonical,
        AsyncMock(),
        ConversationContextPolicy(),
    )
    return ConversationSummaryCompactor(dependencies), session, agent
