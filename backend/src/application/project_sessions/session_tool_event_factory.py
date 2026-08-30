"""Factories for safe, linked TOOL_CALL and TOOL_RESULT events."""

from src.application.project_sessions.session_event_inputs import (
    ToolCallEventInput,
    ToolResultEventInput,
)
from src.domain.project_session.entities import SessionEvent
from src.domain.project_session.enums import AgentType, SessionEventRole, SessionEventType
from src.domain.project_session.value_objects import ToolCallMetadata, ToolResultMetadata


def create_tool_call(data: ToolCallEventInput) -> SessionEvent:
    """Persist allowlisted safe arguments before tool execution."""
    return SessionEvent(
        session_id=data.session_id,
        turn_id=data.turn_id,
        role=SessionEventRole.AGENT,
        type=SessionEventType.TOOL_CALL,
        metadata=ToolCallMetadata(AgentType.DW_DESIGN, data.tool_name, data.arguments),
    )


def create_tool_result(data: ToolResultEventInput) -> SessionEvent:
    """Persist safe result projection linked to its TOOL_CALL."""
    tool = data.call.metadata
    tool_name = tool.tool if isinstance(tool, ToolCallMetadata) else "unknown"
    return SessionEvent(
        session_id=data.call.session_id,
        turn_id=data.call.turn_id,
        role=SessionEventRole.TOOL,
        type=SessionEventType.TOOL_RESULT,
        metadata=ToolResultMetadata(tool_name, data.status, data.call.id, data.result_data, data.error),
    )
