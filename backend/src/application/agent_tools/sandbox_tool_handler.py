"""Sandbox Agent tool adapters composed from existing application ports."""

from dataclasses import replace

from src.application.agent_tools.models import AgentToolPreparation, AgentToolRequest, AgentToolResult
from src.application.data_models.i_data_model_service import IDataModelService
from src.application.data_models.input import GenerateDataModelDdlInput, ResolveDataModelTargetInput
from src.application.sandbox.i_sandbox_service import ISandboxService
from src.application.sandbox.input import ExecuteSandboxDdlInput, GetSandboxConfigInput
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.sandbox.enums import SandboxDbType


class AgentSandboxToolHandler:
    def __init__(self, models: IDataModelService, sandbox: ISandboxService) -> None:
        self._models = models
        self._sandbox = sandbox

    async def prepare(self, data: AgentToolRequest) -> AgentToolPreparation:
        target = await self._models.resolve_target(ResolveDataModelTargetInput(data.project_id, data.target))
        config = await self._sandbox.get_config(GetSandboxConfigInput(data.project_id))
        if config is None:
            return AgentToolPreparation(
                data, False, target.revision,
                message="Project chưa có cấu hình Sandbox.",
                current_revision=target.current_revision or target.revision,
                base_revision=target.base_revision or target.revision,
            )
        return AgentToolPreparation(
            replace(
                data, expected_revision=target.current_revision or target.revision
            ),
            True,
            target.revision,
            config.endpoint_risk,
            config.schema_name,
            current_revision=target.current_revision or target.revision,
            base_revision=target.base_revision or target.revision,
        )

    async def get_config(self, data: AgentToolRequest) -> AgentToolResult:
        config = await self._sandbox.get_config(GetSandboxConfigInput(data.project_id))
        if config is None:
            return AgentToolResult(data.name, False, "Project chưa có Sandbox được cấu hình.")
        return AgentToolResult(
            data.name,
            True,
            "Đã đọc cấu hình Sandbox an toàn.",
            endpoint_risk=config.endpoint_risk,
            schema_name=config.schema_name,
        )

    async def test_connection(self, data: AgentToolRequest) -> AgentToolResult:
        result = await self._sandbox.test_saved_connection(GetSandboxConfigInput(data.project_id))
        return AgentToolResult(data.name, result.success, result.message)

    async def execute(self, data: AgentToolRequest) -> AgentToolResult:
        _require_reset_mode(data)
        ddl = await self._models.generate_ddl(
            GenerateDataModelDdlInput(data.project_id, SandboxDbType.POSTGRESQL, data.target)
        )
        _require_expected_revision(data, ddl.current_revision or ddl.data_model_revision)
        result = await self._sandbox.execute_ddl(ExecuteSandboxDdlInput(data.project_id, ddl.ddl, data.reset_schema))
        return AgentToolResult(
            data.name,
            result.success,
            _execution_summary(result.succeeded_statements, result.executed_statements),
            executed_statements=result.executed_statements,
            succeeded_statements=result.succeeded_statements,
            failed_statements=result.failed_statements,
            total_duration_ms=result.total_duration_ms,
        )


def _require_reset_mode(data: AgentToolRequest) -> None:
    if data.reset_schema is None:
        raise BusinessException(ErrorCode.VALIDATION_ERROR, "Sandbox reset mode chưa được xác nhận.")


def _require_expected_revision(data: AgentToolRequest, revision: int) -> None:
    if data.expected_revision is not None and revision != data.expected_revision:
        raise BusinessException(
            ErrorCode.DATA_MODEL_REVISION_CONFLICT,
            "Data Model đã thay đổi sau khi xác nhận.",
        )


def _execution_summary(succeeded: int, executed: int) -> str:
    return f"Đã chạy {succeeded}/{executed} câu lệnh thành công."
