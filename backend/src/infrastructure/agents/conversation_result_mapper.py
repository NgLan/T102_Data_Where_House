"""Map structured DW conversation output sang application result."""

from src.application.data_warehouse_workflows.output import (
    AgentTurnKind,
    ConversationDesignResult,
    ConversationToolRequest,
)
from src.domain.data_model.enums import DataModelTargetKind
from src.domain.sandbox.enums import SandboxDbType
from src.infrastructure.agents.dbml_normalizer import normalize_agent_dbml
from src.infrastructure.llm.agent_structured_outputs import DwConversationResult


def to_conversation_result(result: DwConversationResult) -> ConversationDesignResult:
    """Ánh xạ đúng discriminator mà không làm rò Pydantic qua boundary."""
    if result.kind == AgentTurnKind.CLARIFICATION:
        return ConversationDesignResult(
            AgentTurnKind.CLARIFICATION,
            question=result.question,
            options=tuple(result.options),
            allow_custom_answer=result.allow_custom_answer,
            reason=result.reason,
            summary=result.summary,
        )
    if result.kind == AgentTurnKind.NO_CHANGE:
        return ConversationDesignResult(
            AgentTurnKind.NO_CHANGE,
            summary=result.summary,
        )
    if result.kind == AgentTurnKind.TOOL_REQUEST:
        return _tool_result(result)
    return ConversationDesignResult(
        AgentTurnKind.PROPOSAL,
        dbml=normalize_agent_dbml(result.dbml or ""),
        summary=result.summary,
    )


def _tool_result(result: DwConversationResult) -> ConversationDesignResult:
    request = ConversationToolRequest(
        result.tool_name or "",
        DataModelTargetKind(result.target_kind or "CURRENT_MODEL"),
        result.proposal_change_id,
        SandboxDbType(result.db_type or "POSTGRESQL"),
        result.reset_schema,
    )
    return ConversationDesignResult(
        AgentTurnKind.TOOL_REQUEST, summary=result.summary, tool_request=request
    )
