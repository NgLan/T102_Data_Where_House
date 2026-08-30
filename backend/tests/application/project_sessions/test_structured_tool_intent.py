"""Permission checks for structured Agent tool decisions."""

from uuid import uuid4

import pytest
from src.application.agent_tools import AgentToolName
from src.application.data_warehouse_workflows.output import ConversationToolRequest
from src.application.project_sessions.structured_tool_intent import (
    StructuredToolIntentInput,
    create_structured_tool_intent,
)
from src.common.exceptions.business import BusinessException
from src.domain.data_model.enums import DataModelTargetKind


def test_structured_tool_name_is_converted_through_allowlist() -> None:
    data = StructuredToolIntentInput(
        uuid4(),
        "Tạo tài liệu phân tích",
        "vi",
        ConversationToolRequest(
            AgentToolName.GENERATE_ANALYSIS,
            DataModelTargetKind.CURRENT_MODEL,
        ),
    )

    intent = create_structured_tool_intent(data)

    assert intent.request.name is AgentToolName.GENERATE_ANALYSIS
    assert intent.requires_confirmation is False


def test_connection_test_requires_direct_user_request() -> None:
    data = StructuredToolIntentInput(
        uuid4(),
        "Sandbox có ổn không?",
        "vi",
        ConversationToolRequest(
            AgentToolName.TEST_SANDBOX_CONNECTION,
            DataModelTargetKind.CURRENT_MODEL,
        ),
    )

    with pytest.raises(BusinessException):
        create_structured_tool_intent(data)
