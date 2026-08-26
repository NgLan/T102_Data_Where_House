"""Pydantic record cho payload JSONB của SessionEvent."""

from pydantic import BaseModel, ConfigDict, Field
from src.domain.project_session.enums import (
    AgentResultStatus,
    AgentType,
    ClarificationAnswerKind,
    ToolResultStatus,
)


class MetadataRecord(BaseModel):
    """Base record cấm trường JSON không thuộc contract."""

    model_config = ConfigDict(extra="forbid")


class MessageRecord(MetadataRecord):
    """Record metadata của message."""

    model: str | None = None
    agent_result_id: str | None = None
    proposal_change_id: str | None = None


class ClarificationQuestionRecord(MetadataRecord):
    """Record metadata của câu hỏi clarification."""

    options: list[str] = Field(min_length=1, max_length=4)
    allow_custom_answer: bool
    reason: str | None = None
    original_intent: str | None = None
    missing_information: str | None = None


class ClarificationAnswerRecord(MetadataRecord):
    """Record liên kết answer với question nguồn."""

    question_id: str
    kind: ClarificationAnswerKind
    option_index: int | None = None


class AgentCallRecord(MetadataRecord):
    """Record metadata của agent call."""

    caller_agent: AgentType
    target_agent: AgentType
    input: str


class LlmRecord(MetadataRecord):
    """Record thống kê một lần gọi LLM."""

    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    temperature: float
    latency_ms: int
    finish_reason: str | None = None


class AgentResultRecord(MetadataRecord):
    """Record metadata của agent result."""

    session_event_id: str
    agent: AgentType
    status: AgentResultStatus
    output: str | None = None
    error: str | None = None
    llm: LlmRecord | None = None


class ToolCallRecord(MetadataRecord):
    """Record metadata của tool call."""

    agent: AgentType
    tool: str
    arguments: str | None = None


class ToolResultRecord(MetadataRecord):
    """Record metadata của tool result."""

    session_event_id: str
    tool: str
    status: ToolResultStatus
    result: str | None = None
    error: str | None = None
