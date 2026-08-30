"""Ordered persistence and execution for one allowlisted Agent tool."""

from dataclasses import dataclass

from src.application.agent_tools import AgentToolPreparation, AgentToolRequest, AgentToolResult, IAgentToolService
from src.application.data_warehouse_workflows.output import AgentTurnKind
from src.application.project_sessions.output import SessionTurnOutput
from src.application.project_sessions.session_event_factory import (
    AgentMessageEventInput,
    AgentResultEventInput,
    create_agent_message,
    create_agent_result,
)
from src.application.project_sessions.session_event_inputs import (
    ToolCallEventInput,
    ToolResultEventInput,
)
from src.application.project_sessions.session_tool_event_factory import (
    create_tool_call,
    create_tool_result,
)
from src.application.project_sessions.session_tool_event_writer import SessionToolEventWriter
from src.application.project_sessions.session_tool_payloads import safe_tool_arguments, safe_tool_result
from src.common.utils.json import safe_json_dumps
from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.project_session.enums import AgentResultStatus, ToolResultStatus


@dataclass(frozen=True, slots=True)
class ToolExecutionDependencies:
    tools: IAgentToolService
    writer: SessionToolEventWriter


@dataclass(frozen=True, slots=True)
class ToolCompletionInput:
    session: ProjectSession
    agent_call: SessionEvent
    tool_call: SessionEvent
    result: AgentToolResult


class SessionToolExecution:
    def __init__(self, dependencies: ToolExecutionDependencies) -> None:
        self._dependencies = dependencies

    async def execute(
        self, session: ProjectSession, agent_call: SessionEvent, request: AgentToolRequest
    ) -> SessionTurnOutput:
        tool_call = await self._persist_call(session, agent_call, request)
        try:
            result = await self._dependencies.tools.execute(request)
        except Exception:
            result = AgentToolResult(request.name, False, "Tool không thể hoàn tất thao tác này.")
        return await self._complete(ToolCompletionInput(session, agent_call, tool_call, result))

    async def complete_unready(
        self, session: ProjectSession, agent_call: SessionEvent, prepared: AgentToolPreparation
    ) -> SessionTurnOutput:
        result = AgentToolResult(
            prepared.request.name,
            False,
            prepared.message or "Tool chưa sẵn sàng.",
        )
        call = await self._persist_call(session, agent_call, prepared.request)
        return await self._complete(ToolCompletionInput(session, agent_call, call, result))

    async def cancel(self, session: ProjectSession, agent_call: SessionEvent) -> SessionTurnOutput:
        if agent_call.turn_id is None:
            raise ValueError("Agent call must have a turn ID.")
        summary = "Đã hủy thao tác."
        result = create_agent_result(AgentResultEventInput(agent_call, AgentResultStatus.CANCELLED, summary))
        message = create_agent_message(AgentMessageEventInput(result, summary))
        session.release_turn(agent_call.turn_id)
        await self._dependencies.writer.persist(session, (result, message))
        return SessionTurnOutput(session.id, agent_call.turn_id, AgentTurnKind.CANCELLED, summary=summary)

    async def _persist_call(
        self, session: ProjectSession, agent_call: SessionEvent, request: AgentToolRequest
    ) -> SessionEvent:
        if agent_call.turn_id is None:
            raise ValueError("Agent call must have a turn ID.")
        event = create_tool_call(
            ToolCallEventInput(
                session.id,
                agent_call.turn_id,
                request.name,
                safe_json_dumps(safe_tool_arguments(request)),
            )
        )
        await self._dependencies.writer.persist(session, (event,))
        return event

    async def _complete(self, data: ToolCompletionInput) -> SessionTurnOutput:
        session, agent_call = data.session, data.agent_call
        tool_call, result = data.tool_call, data.result
        tool_status = ToolResultStatus.SUCCESS if result.success else ToolResultStatus.FAILED
        tool_result = create_tool_result(
            ToolResultEventInput(tool_call, tool_status, safe_json_dumps(safe_tool_result(result)))
        )
        agent_status = AgentResultStatus.SUCCESS if result.success else AgentResultStatus.FAILED
        agent_result = create_agent_result(AgentResultEventInput(agent_call, agent_status, result.summary))
        message = create_agent_message(AgentMessageEventInput(agent_result, result.summary))
        if agent_call.turn_id is None:
            raise ValueError("Agent call must have a turn ID.")
        session.release_turn(agent_call.turn_id)
        await self._dependencies.writer.persist(session, (tool_result, agent_result, message))
        return SessionTurnOutput(
            session.id,
            agent_call.turn_id,
            AgentTurnKind.TOOL_RESULT,
            summary=result.summary,
            tool_name=result.name,
            tool_status=tool_status,
            artifact_event_id=tool_result.id if result.artifact else None,
        )
