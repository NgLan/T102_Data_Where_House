"""Pause/resume coordinator cho clarification của một Agent turn."""

from src.application.data_warehouse_workflows.input import CreateAgentTurnInput
from src.application.data_warehouse_workflows.output import AgentTurnOutput
from src.application.project_sessions.clarification_answer import (
    raise_stale_clarification,
    resolve_clarification_answer,
)
from src.application.project_sessions.clarification_context import (
    create_clarification_memory_input,
)
from src.application.project_sessions.clarification_output import ClarificationQuestionOutput
from src.application.project_sessions.input import AnswerClarificationInput, GetPendingClarificationInput
from src.application.project_sessions.output import SessionTurnOutput
from src.application.project_sessions.session_access import ensure_session_purpose
from src.application.project_sessions.session_clarification_dependencies import (
    ClarificationDependencies,
)
from src.application.project_sessions.session_event_factory import (
    AnswerEventInput,
    create_agent_call,
    create_answer,
)
from src.application.project_sessions.session_turn_completion import (
    SessionTurnCompletion,
    TurnCompletionDependencies,
)
from src.application.project_sessions.session_turn_history import TURN_STALE_AFTER
from src.common.utils.datetime import utc_now
from src.domain.project_session.clarification import ClarificationQuestionMetadata
from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.project_session.enums import SessionEventType, SessionPurpose
from src.domain.shared.types import EntityID


class SessionClarificationCoordinator:
    """Chấp nhận đúng một answer rồi tiếp tục Agent turn đang chờ."""

    def __init__(self, dependencies: ClarificationDependencies) -> None:
        self._dependencies = dependencies
        self._completion = SessionTurnCompletion(
            TurnCompletionDependencies(dependencies.sessions, dependencies.events, dependencies.unit_of_work)
        )

    async def get_pending(self, data: GetPendingClarificationInput) -> ClarificationQuestionOutput | None:
        session = await self._dependencies.access.require(data.session_id)
        ensure_session_purpose(session, SessionPurpose.DATA_MODELING)
        if session.pending_question_id is None:
            return None
        question = await self._require_question(session, session.pending_question_id)
        return ClarificationQuestionOutput.from_domain(question)

    async def answer(self, data: AnswerClarificationInput) -> SessionTurnOutput:
        start = await self._begin(data)
        session, _, call, _ = start
        try:
            result = await self._run_agent(start)
        except Exception:
            await self._completion.fail(session, call)
            raise
        output = await self._completion.complete(session, call, result)
        await self._dependencies.context.compact_after_completion(
            session.id, session.project_id
        )
        return output

    async def _run_agent(
        self,
        start: tuple[ProjectSession, SessionEvent, SessionEvent, str],
    ) -> AgentTurnOutput:
        session, question, call, content = start
        memory_input, original_intent = create_clarification_memory_input(
            session, question, content
        )
        memory = await self._dependencies.context.build_memory(memory_input)
        return await self._dependencies.workflow.create_agent_turn(
            CreateAgentTurnInput(
                session.project_id,
                content,
                memory,
                turn_id=call.turn_id,
                original_intent=original_intent,
            )
        )

    async def _begin(self, data: AnswerClarificationInput) -> tuple[ProjectSession, SessionEvent, SessionEvent, str]:
        dependencies = self._dependencies
        async with dependencies.unit_of_work:
            session = await dependencies.access.require(data.session_id, for_update=True)
            ensure_session_purpose(session, SessionPurpose.DATA_MODELING)
            question = await self._require_question(session, data.question_id)
            content, kind, option_index = resolve_clarification_answer(question, data)
            if question.turn_id is None:
                raise_stale_clarification()
            session.resume_turn(data.question_id, question.turn_id, utc_now() - TURN_STALE_AFTER)
            answer = create_answer(
                AnswerEventInput(session.id, question.turn_id, question.id, content, kind, option_index)
            )
            call = create_agent_call(session.id, question.turn_id)
            await dependencies.sessions.save(session)
            await dependencies.events.save(answer)
            await dependencies.events.save(call)
            await dependencies.unit_of_work.commit()
        return session, question, call, content

    async def _require_question(self, session: ProjectSession, question_id: EntityID) -> SessionEvent:
        if session.pending_question_id != question_id:
            raise_stale_clarification()
        question = await self._dependencies.events.get_by_id(question_id)
        if (
            question is None
            or question.session_id != session.id
            or question.type is not SessionEventType.QUESTION
            or not isinstance(question.metadata, ClarificationQuestionMetadata)
        ):
            raise_stale_clarification()
        return question
