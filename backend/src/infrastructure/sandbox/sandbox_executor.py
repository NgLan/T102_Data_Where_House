"""Application adapter cho PostgreSQL Sandbox."""

import asyncpg
from src.application.sandbox.i_sandbox_service import ISandboxExecutor
from src.application.sandbox.input import SandboxConnectionInput
from src.application.sandbox.output import ConnectionTestOutput, SandboxExecutionOutput
from src.domain.sandbox.entities import SandboxConfig
from src.infrastructure.sandbox.postgres_connection import check_connection
from src.infrastructure.sandbox.postgres_ddl_executor import execute_sandbox_ddl
from src.infrastructure.sandbox.postgres_ddl_validator import split_ddl_statements
from typing_extensions import override


async def check_sandbox_connection(data: SandboxConnectionInput) -> tuple[bool, str, float]:
    """Kiểm tra kết nối PostgreSQL với thông báo đã làm sạch."""
    return await check_connection(data)


class PostgresSandboxExecutor(ISandboxExecutor):
    """Implement Application executor port cho PostgreSQL."""

    @override
    async def test_connection(self, settings: SandboxConnectionInput) -> ConnectionTestOutput:
        """Kiểm tra kết nối mà không thay đổi database."""
        success, message, latency = await check_sandbox_connection(settings)
        return ConnectionTestOutput(success, message, latency)

    @override
    async def execute(
        self,
        config: SandboxConfig,
        ddl_script: str,
        reset_schema: bool,
    ) -> SandboxExecutionOutput:
        """Thực thi DDL đã được Application yêu cầu."""
        return await execute_sandbox_ddl(config, ddl_script, reset_schema)


__all__ = [
    "PostgresSandboxExecutor",
    "asyncpg",
    "check_sandbox_connection",
    "execute_sandbox_ddl",
    "split_ddl_statements",
]
