"""Authorization adapter from structured Agent decisions to tool registry inputs."""

from dataclasses import dataclass

from src.application.agent_tools import (
    AgentToolIntent,
    AgentToolName,
    AgentToolRequest,
    parse_agent_tool_intent,
)
from src.application.data_models.input import DataModelTargetInput
from src.application.data_warehouse_workflows.output import ConversationToolRequest
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class StructuredToolIntentInput:
    project_id: EntityID
    content: str
    locale: str
    request: ConversationToolRequest


def create_structured_tool_intent(
    data: StructuredToolIntentInput,
) -> AgentToolIntent:
    """Convert only allowlisted typed fields and enforce direct connection-test intent."""
    name = AgentToolName(data.request.name)
    _require_direct_connection_test(data, name)
    target = DataModelTargetInput(data.request.target_kind, data.request.proposal_change_id)
    request = AgentToolRequest(
        data.project_id,
        name,
        target,
        data.request.db_type,
        data.request.reset_schema,
        data.locale,
    )
    return AgentToolIntent(request, requires_confirmation=name is AgentToolName.EXECUTE_SANDBOX_DDL)


def _require_direct_connection_test(data: StructuredToolIntentInput, name: AgentToolName) -> None:
    if name is not AgentToolName.TEST_SANDBOX_CONNECTION:
        return
    explicit = parse_agent_tool_intent(data.project_id, data.content, data.locale)
    if explicit is None or explicit.request.name is not name:
        raise BusinessException(
            ErrorCode.VALIDATION_ERROR,
            "Connection test chỉ được chạy khi người dùng yêu cầu trực tiếp.",
        )
