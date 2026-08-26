"""Module quản lý Phiên Agent (Agent Session Domain)."""

from src.domain.project_session.clarification import (
    ClarificationAnswerMetadata,
    ClarificationQuestionMetadata,
)
from src.domain.project_session.conversation_summary import (
    ConversationSummary,
    ConversationSummaryUpdate,
    ResolvedClarification,
    SummaryDecision,
    SummaryItem,
)
from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.project_session.enums import (
    AgentResultStatus,
    AgentType,
    ClarificationAnswerKind,
    SessionEventRole,
    SessionEventType,
    SessionStatus,
    ToolResultStatus,
)
from src.domain.project_session.i_project_session_repository import IProjectSessionRepository
from src.domain.project_session.i_session_event_repository import ISessionEventRepository
from src.domain.project_session.rules import (
    validate_session_event_ref,
    validate_session_event_shape,
    validate_session_metadata,
)
from src.domain.project_session.value_objects import (
    AgentCallMetadata,
    AgentResultMetadata,
    LLMCallStats,
    MessageMetadata,
    SessionEventMetadata,
    ToolCallMetadata,
    ToolResultMetadata,
)

__all__: list[str] = [
    "ProjectSession",
    "SessionEvent",
    "SessionStatus",
    "SessionEventRole",
    "SessionEventType",
    "AgentType",
    "ClarificationAnswerKind",
    "AgentResultStatus",
    "ToolResultStatus",
    "SessionEventMetadata",
    "MessageMetadata",
    "ClarificationQuestionMetadata",
    "ClarificationAnswerMetadata",
    "ConversationSummary",
    "ConversationSummaryUpdate",
    "SummaryItem",
    "SummaryDecision",
    "ResolvedClarification",
    "AgentCallMetadata",
    "AgentResultMetadata",
    "ToolCallMetadata",
    "ToolResultMetadata",
    "LLMCallStats",
    "IProjectSessionRepository",
    "ISessionEventRepository",
    "validate_session_event_ref",
    "validate_session_event_shape",
    "validate_session_metadata",
]
