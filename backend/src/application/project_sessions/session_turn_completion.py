"""Persists the public result of an Agent turn."""

from dataclasses import dataclass

from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_warehouse_workflows.output import (
    AgentTurnKind,
    AgentTurnOutput,
)
from src.application.project_sessions.output import SessionTurnOutput
from src.application.project_sessions.session_event_factory import (
    AgentMessageEventInput,
    AgentResultEventInput,
    create_agent_message,
    create_agent_result,
)
from src.application.project_sessions.session_question_completion import (
    create_question_event,
    create_question_turn_output,
)
from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.project_session.enums import AgentResultStatus
from src.domain.project_session.i_project_session_repository import (
    IProjectSessionRepository,
)
from src.domain.project_session.i_session_event_repository import (
    ISessionEventRepository,
)
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class TurnCompletionDependencies:
    sessions: IProjectSessionRepository
    events: ISessionEventRepository
    unit_of_work: IUnitOfWork


class SessionTurnCompletion:
    def __init__(self, dependencies: TurnCompletionDependencies) -> None:
        self._dependencies = dependencies

    async def fail(self, session: ProjectSession, call: SessionEvent) -> None:
        await self._finish(
            session,
            call.turn_id,
            (
                create_agent_result(
                    AgentResultEventInput(call, AgentResultStatus.FAILED, "Agent could not complete this turn.")
                ),
            ),
        )

    async def complete(
        self,
        session: ProjectSession,
        call: SessionEvent,
        result: AgentTurnOutput,
    ) -> SessionTurnOutput:
        if result.kind is AgentTurnKind.CLARIFICATION:
            return await self._complete_question(session, call, result)
        events, change_id = _success_events(call, result)
        await self._finish(session, call.turn_id, events)
        return SessionTurnOutput(
            session.id,
            call.turn_id,
            result.kind,
            proposal_change_id=change_id,
            summary=result.summary,
        )

    async def _complete_question(
        self,
        session: ProjectSession,
        call: SessionEvent,
        result: AgentTurnOutput,
    ) -> SessionTurnOutput:
        event = create_question_event(session, call, result)
        if call.turn_id is None:  # Narrow type cho domain transition.
            raise ValueError("Agent call must have a turn ID.")
        session.wait_for_clarification(call.turn_id, event.id)
        await self._persist(session, (event,))
        return create_question_turn_output(session, event, result)

    async def _finish(
        self,
        session: ProjectSession,
        turn_id: EntityID | None,
        events: tuple[SessionEvent, ...],
    ) -> None:
        if turn_id is None:
            return
        session.release_turn(turn_id)
        await self._persist(session, events)

    async def _persist(
        self,
        session: ProjectSession,
        events: tuple[SessionEvent, ...],
    ) -> None:
        dependencies = self._dependencies
        async with dependencies.unit_of_work:
            for event in events:
                await dependencies.events.save(event)
            await dependencies.sessions.save(session)
            await dependencies.unit_of_work.commit()


def _default_success_message(kind: AgentTurnKind) -> str:
    """Cung cấp nội dung an toàn khi application output thiếu summary."""
    if kind is AgentTurnKind.NO_CHANGE:
        return "The current Data Model already satisfies this request."
    return "The proposal is ready for review."


def _success_events(call: SessionEvent, result: AgentTurnOutput) -> tuple[tuple[SessionEvent, ...], EntityID | None]:
    """Tạo technical result và đúng một public Agent message."""
    change_id = result.proposal.summary.id if result.proposal else None
    content = result.summary or _default_success_message(result.kind)
    event = create_agent_result(
        AgentResultEventInput(
            call,
            AgentResultStatus.SUCCESS,
            content,
            str(change_id) if change_id else None,
        )
    )
    message = create_agent_message(AgentMessageEventInput(event, content, change_id))
    return (event, message), change_id
