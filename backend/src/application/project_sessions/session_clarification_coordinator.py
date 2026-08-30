"""Pause/resume coordinator cho clarification của một Agent turn."""

from src.application.data_warehouse_workflows.input import CreateAgentTurnInput
from src.application.data_warehouse_workflows.output import AgentTurnOutput
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
from src.application.project_sessions.session_clarification_state import (
    ClarificationStateDependencies,
    SessionClarificationState,
)
from src.application.project_sessions.session_tool_coordinator import (
    SessionToolCoordinator,
    SessionToolDependencies,
    ToolResumeInput,
)
from src.application.project_sessions.session_turn_completion import (
    SessionTurnCompletion,
    TurnCompletionDependencies,
)
from src.domain.project_session.clarification import ClarificationQuestionMetadata
from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.project_session.enums import (
    SessionPurpose,
    SessionQuestionKind,
)


class SessionClarificationCoordinator:
    """Chấp nhận đúng một answer rồi tiếp tục Agent turn đang chờ."""

    def __init__(self, dependencies: ClarificationDependencies) -> None:
        self._dependencies = dependencies
        self._state = SessionClarificationState(
            ClarificationStateDependencies(
                dependencies.sessions,
                dependencies.events,
                dependencies.unit_of_work,
                dependencies.access,
            )
        )
        self._completion = SessionTurnCompletion(
            TurnCompletionDependencies(dependencies.sessions, dependencies.events, dependencies.unit_of_work)
        )
        self._tools = (
            SessionToolCoordinator(
                SessionToolDependencies(
                    dependencies.sessions,
                    dependencies.events,
                    dependencies.unit_of_work,
                    dependencies.tools,
                )
            )
            if dependencies.tools
            else None
        )

    async def get_pending(self, data: GetPendingClarificationInput) -> ClarificationQuestionOutput | None:
        session = await self._dependencies.access.require(data.session_id)
        ensure_session_purpose(session, SessionPurpose.DATA_MODELING)
        if session.pending_question_id is None:
            return None
        question = await self._state.require_question(session, session.pending_question_id)
        return ClarificationQuestionOutput.from_domain(question)

    async def answer(self, data: AnswerClarificationInput) -> SessionTurnOutput:
        start = await self._state.begin(data)
        session, question, call, _ = start
        metadata = question.metadata
        if (
            isinstance(metadata, ClarificationQuestionMetadata)
            and metadata.question_kind is not SessionQuestionKind.CLARIFICATION
            and self._tools is not None
        ):
            return await self._tools.resume(ToolResumeInput(session, question, call, data.option_index))
        try:
            result = await self._run_agent(start)
        except Exception:
            await self._completion.fail(session, call)
            raise
        output = await self._completion.complete(session, call, result)
        await self._dependencies.context.compact_after_completion(session.id, session.project_id)
        return output

    async def _run_agent(
        self,
        start: tuple[ProjectSession, SessionEvent, SessionEvent, str],
    ) -> AgentTurnOutput:
        session, question, call, content = start
        memory_input, original_intent = create_clarification_memory_input(session, question, content)
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
