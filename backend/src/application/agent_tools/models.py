"""Typed contracts cho Modeling Agent tools."""

from dataclasses import dataclass
from enum import StrEnum

from src.application.data_models.input import DataModelTargetInput
from src.domain.data_model.enums import DataModelTargetKind
from src.domain.sandbox.enums import SandboxDbType, SandboxEndpointRisk
from src.domain.shared.types import EntityID


class AgentToolName(StrEnum):
    GENERATE_ANALYSIS = "generate_data_model_analysis_document"
    GENERATE_DDL = "generate_data_model_ddl"
    GET_SANDBOX_CONFIG = "get_sandbox_config"
    TEST_SANDBOX_CONNECTION = "test_sandbox_connection"
    EXECUTE_SANDBOX_DDL = "execute_sandbox_ddl"


@dataclass(frozen=True, slots=True)
class AgentToolRequest:
    project_id: EntityID
    name: AgentToolName
    target: DataModelTargetInput = DataModelTargetInput()
    db_type: SandboxDbType = SandboxDbType.POSTGRESQL
    reset_schema: bool | None = None
    locale: str = "vi"
    expected_revision: int | None = None


@dataclass(frozen=True, slots=True)
class ToolArtifact:
    id: EntityID
    filename: str
    storage_filename: str
    mime_type: str
    data_model_revision: int
    target_kind: DataModelTargetKind
    proposal_change_id: EntityID | None = None
    current_revision: int | None = None
    base_revision: int | None = None


@dataclass(frozen=True, slots=True)
class AgentToolResult:
    name: AgentToolName
    success: bool
    summary: str
    artifact: ToolArtifact | None = None
    endpoint_risk: SandboxEndpointRisk | None = None
    schema_name: str | None = None
    executed_statements: int | None = None
    succeeded_statements: int | None = None
    failed_statements: int | None = None
    total_duration_ms: float | None = None


@dataclass(frozen=True, slots=True)
class AgentToolIntent:
    request: AgentToolRequest
    requires_confirmation: bool = False


@dataclass(frozen=True, slots=True)
class AgentToolPreparation:
    """Safe state dùng để dựng confirmation, không chứa credential hay DDL."""

    request: AgentToolRequest
    ready: bool
    revision: int
    endpoint_risk: SandboxEndpointRisk | None = None
    schema_name: str | None = None
    message: str | None = None
    current_revision: int | None = None
    base_revision: int | None = None
