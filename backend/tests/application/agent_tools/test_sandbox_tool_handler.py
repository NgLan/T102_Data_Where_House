"""Revision guards for the Sandbox Agent tool adapter."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.application.agent_tools.models import AgentToolName, AgentToolRequest
from src.application.agent_tools.sandbox_tool_handler import AgentSandboxToolHandler
from src.application.data_models.input import DataModelTargetInput
from src.application.data_models.output import DataModelDdlOutput
from src.common.exceptions.business import BusinessException
from src.domain.data_model.enums import DataModelTargetKind
from src.domain.sandbox.enums import SandboxDbType


@pytest.mark.asyncio
async def test_stale_current_revision_never_executes_proposal_ddl() -> None:
    project_id = uuid4()
    models = AsyncMock()
    models.generate_ddl.return_value = DataModelDdlOutput(
        "CREATE TABLE stale (id int);",
        SandboxDbType.POSTGRESQL,
        2,
        DataModelTargetKind.PROPOSAL,
        uuid4(),
        current_revision=4,
        base_revision=2,
    )
    sandbox = AsyncMock()
    handler = AgentSandboxToolHandler(models, sandbox)
    request = AgentToolRequest(
        project_id,
        AgentToolName.EXECUTE_SANDBOX_DDL,
        DataModelTargetInput(DataModelTargetKind.PROPOSAL),
        reset_schema=False,
        expected_revision=3,
    )

    with pytest.raises(BusinessException):
        await handler.execute(request)

    sandbox.execute_ddl.assert_not_awaited()
