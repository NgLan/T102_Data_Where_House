"""Output models độc lập HTTP cho Sandbox application service."""

from dataclasses import dataclass

from src.domain.sandbox.entities import SandboxConfig
from src.domain.sandbox.enums import SandboxDbType
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class SandboxConfigOutput:
    id: EntityID
    project_id: EntityID
    db_type: SandboxDbType
    host: str
    port: int
    database_name: str
    username: str | None
    schema_name: str | None
    status: str = "CONFIGURED"

    @classmethod
    def from_domain(cls, config: SandboxConfig) -> "SandboxConfigOutput":
        """Ánh xạ config entity mà không làm lộ password."""
        return cls(
            config.id,
            config.project_id,
            config.db_type,
            config.host,
            config.port,
            config.database_name,
            config.username,
            config.schema_name,
        )


@dataclass(frozen=True, slots=True)
class ConnectionTestOutput:
    success: bool
    message: str
    latency_ms: float | None = None


@dataclass(frozen=True, slots=True)
class StatementExecutionOutput:
    statement: str
    is_success: bool
    execution_time_ms: float
    timestamp: str
    error_detail: str | None = None


@dataclass(frozen=True, slots=True)
class SandboxExecutionOutput:
    success: bool
    executed_statements: int
    succeeded_statements: int
    failed_statements: int
    total_duration_ms: float
    logs: tuple[StatementExecutionOutput, ...] = ()
