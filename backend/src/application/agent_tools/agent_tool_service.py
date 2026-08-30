"""Closed registry for Modeling Agent tools."""

from src.application.agent_tools.artifact_tool_handler import AgentArtifactToolHandler
from src.application.agent_tools.i_agent_tool_service import IAgentToolService
from src.application.agent_tools.models import (
    AgentToolName,
    AgentToolPreparation,
    AgentToolRequest,
    AgentToolResult,
)
from src.application.agent_tools.sandbox_tool_handler import AgentSandboxToolHandler
from src.application.common.i_file_store import IFileStore
from src.application.data_model_analysis import IDataModelAnalysisService
from src.application.data_models.i_data_model_service import IDataModelService
from src.application.sandbox.i_sandbox_service import ISandboxService
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from typing_extensions import override


class AgentToolService(IAgentToolService):
    """LLM-selected names still pass through this exact allowlist."""

    def __init__(
        self,
        models: IDataModelService,
        analysis: IDataModelAnalysisService,
        sandbox: ISandboxService,
        files: IFileStore,
    ) -> None:
        self._artifacts = AgentArtifactToolHandler(models, analysis, files)
        self._sandbox = AgentSandboxToolHandler(models, sandbox)

    @override
    async def prepare(self, data: AgentToolRequest) -> AgentToolPreparation:
        return await self._sandbox.prepare(data)

    @override
    async def execute(self, data: AgentToolRequest) -> AgentToolResult:
        handlers = {
            AgentToolName.GENERATE_ANALYSIS: self._artifacts.generate_analysis,
            AgentToolName.GENERATE_DDL: self._artifacts.generate_ddl,
            AgentToolName.GET_SANDBOX_CONFIG: self._sandbox.get_config,
            AgentToolName.TEST_SANDBOX_CONNECTION: self._sandbox.test_connection,
            AgentToolName.EXECUTE_SANDBOX_DDL: self._sandbox.execute,
        }
        handler = handlers.get(data.name)
        if handler is None:
            raise BusinessException(ErrorCode.VALIDATION_ERROR, "Agent tool không được cấp quyền.")
        return await handler(data)

    @override
    async def read_artifact(self, storage_path: str) -> bytes:
        return await self._artifacts.read(storage_path)
