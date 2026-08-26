"""Map structured DW conversation output sang application result."""

from src.application.data_warehouse_workflows.output import (
    AgentTurnKind,
    ConversationDesignResult,
)
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
    return ConversationDesignResult(
        AgentTurnKind.PROPOSAL,
        dbml=normalize_agent_dbml(result.dbml or ""),
        summary=result.summary,
    )
