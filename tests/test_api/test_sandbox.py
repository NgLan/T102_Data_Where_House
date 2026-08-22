"""API contract tests cho cấu hình và thực thi Sandbox."""

from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest
from main import app
from src.application.sandbox.i_sandbox_service import ISandboxService
from src.application.sandbox.output import (
    ConnectionTestOutput,
    SandboxConfigOutput,
    SandboxExecutionOutput,
)
from src.domain.sandbox.enums import SandboxDbType
from src.presentation.dependencies.sandbox import get_sandbox_service

PROJECT_ID = UUID("86fd6b4e-1822-42db-a847-4d580abead3e")


@pytest.mark.asyncio
async def test_get_missing_sandbox_config_returns_null(client) -> None:
    service = AsyncMock(spec=ISandboxService)
    service.get_config.return_value = None
    app.dependency_overrides[get_sandbox_service] = lambda: service
    try:
        response = await client.get(f"/api/v1/projects/{PROJECT_ID}/sandbox/config")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["data"] is None


@pytest.mark.asyncio
async def test_save_sandbox_config_contract(client) -> None:
    service = AsyncMock(spec=ISandboxService)
    service.save_config.return_value = SandboxConfigOutput(
        id=uuid4(),
        project_id=PROJECT_ID,
        db_type=SandboxDbType.POSTGRESQL,
        host="localhost",
        port=5432,
        database_name="sandbox_db",
        username="postgres",
        schema_name="public",
    )
    app.dependency_overrides[get_sandbox_service] = lambda: service
    try:
        response = await client.post(
            f"/api/v1/projects/{PROJECT_ID}/sandbox/config",
            json={
                "db_type": "POSTGRESQL",
                "host": "localhost",
                "port": 5432,
                "database_name": "sandbox_db",
                "username": "postgres",
                "password": "secret",
                "schema_name": "public",
            },
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert "password" not in response.json()["data"]


@pytest.mark.asyncio
async def test_execute_sandbox_ddl_failure_contract(client) -> None:
    service = AsyncMock(spec=ISandboxService)
    service.execute_ddl.return_value = SandboxExecutionOutput(
        success=False,
        executed_statements=0,
        succeeded_statements=0,
        failed_statements=0,
        total_duration_ms=1,
        logs=(),
    )
    app.dependency_overrides[get_sandbox_service] = lambda: service
    try:
        response = await client.post(
            f"/api/v1/projects/{PROJECT_ID}/sandbox/execute-ddl",
            json={"ddl_script": "CREATE TABLE users (id INT);"},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["data"]["success"] is False


@pytest.mark.asyncio
async def test_connection_is_project_scoped(client) -> None:
    service = AsyncMock(spec=ISandboxService)
    service.test_connection.return_value = ConnectionTestOutput(True, "ok", 2)
    app.dependency_overrides[get_sandbox_service] = lambda: service
    try:
        response = await client.post(
            f"/api/v1/projects/{PROJECT_ID}/sandbox/test-connection",
            json={
                "db_type": "POSTGRESQL",
                "host": "localhost",
                "port": 5432,
                "database_name": "sandbox_db",
            },
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["data"]["success"] is True
    assert service.test_connection.await_args.args[0].project_id == PROJECT_ID


@pytest.mark.asyncio
async def test_sandbox_rejects_unsupported_engine_before_service(client) -> None:
    service = AsyncMock(spec=ISandboxService)
    app.dependency_overrides[get_sandbox_service] = lambda: service
    try:
        response = await client.post(
            f"/api/v1/projects/{PROJECT_ID}/sandbox/config",
            json={
                "db_type": "MYSQL",
                "host": "localhost",
                "port": 3306,
                "database_name": "sandbox_db",
            },
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 422
    service.save_config.assert_not_awaited()
