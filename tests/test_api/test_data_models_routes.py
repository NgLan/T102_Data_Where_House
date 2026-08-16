"""Integration tests cho Data Models API Router (GET & PUT /api/v1/projects/{project_id}/data-model)."""

from uuid import uuid4

import pytest
from main import app
from src.application.data_models.dto import DataModelDto
from src.application.data_models.IGetDataModelService import IGetDataModelService
from src.application.data_models.IUpdateDataModelService import (
    IUpdateDataModelService,
)
from src.domain.user.entities import User
from src.presentation.dependencies.application import (
    get_data_model_service,
    get_update_data_model_service,
)
from src.presentation.dependencies.auth import get_current_user


class DummyGetDataModelService(IGetDataModelService):
    """Fake GetDataModelService cho route test."""

    async def execute(self, project_id: object) -> DataModelDto | None:
        return DataModelDto(
            id=uuid4(),
            project_id=project_id,  # type: ignore[arg-type]
            dbml="Table Users { id uuid [pk] }",
            revision=1,
            created_at="2026-08-15T00:00:00Z",
            updated_at="2026-08-15T00:00:00Z",
        )


class DummyUpdateDataModelService(IUpdateDataModelService):
    """Fake UpdateDataModelService cho route test."""

    async def execute(self, command: object) -> DataModelDto:
        return DataModelDto(
            id=uuid4(),
            project_id=command.project_id,  # type: ignore[attr-defined]
            dbml=command.dbml,  # type: ignore[attr-defined]
            revision=2,
            created_at="2026-08-15T00:00:00Z",
            updated_at="2026-08-15T00:01:00Z",
        )


def get_mock_current_user() -> User:
    """Trả về Mock User cho test."""
    return User(
        id=uuid4(),
        username="test_user",
        email="test@example.com",  # type: ignore[arg-type]
    )


@pytest.mark.asyncio
async def test_get_data_model_endpoint(client) -> None:
    """Kiểm tra gọi GET /api/v1/projects/{id}/data-model trả về 200 OK và ApiResponse chuẩn."""
    app.dependency_overrides[get_data_model_service] = lambda: DummyGetDataModelService()
    app.dependency_overrides[get_current_user] = get_mock_current_user

    project_id = uuid4()
    response = await client.get(f"/api/v1/projects/{project_id}/data-model")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "success"
    assert json_data["data"]["dbml"] == "Table Users { id uuid [pk] }"
    assert json_data["data"]["revision"] == 1


@pytest.mark.asyncio
async def test_put_data_model_endpoint(client) -> None:
    """Kiểm tra gọi PUT /api/v1/projects/{id}/data-model cập nhật DBML thành công."""
    app.dependency_overrides[get_update_data_model_service] = lambda: DummyUpdateDataModelService()
    app.dependency_overrides[get_current_user] = get_mock_current_user

    project_id = uuid4()
    payload = {"dbml": "Table Rides { ride_id int [pk] }", "expected_revision": 1}
    response = await client.put(f"/api/v1/projects/{project_id}/data-model", json=payload)

    app.dependency_overrides.clear()

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "success"
    assert json_data["data"]["dbml"] == "Table Rides { ride_id int [pk] }"
    assert json_data["data"]["revision"] == 2
