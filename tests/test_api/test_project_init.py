"""API contract test cho project khởi tạo UUID thật."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from main import app
from src.application.projects.i_project_service import IProjectService
from src.application.projects.output import ProjectOutput
from src.presentation.dependencies.projects import get_project_service


@pytest.mark.asyncio
async def test_create_project_contract(client) -> None:
    project_id = uuid4()
    service = AsyncMock(spec=IProjectService)
    service.create_project.return_value = ProjectOutput(
        project_id=project_id,
        domain="ride",
        target_dialect="postgresql",
        status="ACTIVE",
        created_at=datetime.now(UTC),
    )
    app.dependency_overrides[get_project_service] = lambda: service
    try:
        response = await client.post(
            "/api/v1/projects/init",
            json={
                "domain": "ride",
                "target_dialect": "postgresql",
                "business_description": "Phân tích chuyến đi",
                "is_masking_enabled": True,
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["data"]["project_id"] == str(project_id)
    service.create_project.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_project_rejects_unsupported_dialect(client) -> None:
    service = AsyncMock(spec=IProjectService)
    app.dependency_overrides[get_project_service] = lambda: service
    try:
        response = await client.post(
            "/api/v1/projects/init",
            json={"domain": "ride", "target_dialect": "snowflake"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    service.create_project.assert_not_awaited()
