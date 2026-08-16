"""API contract tests cho DDL và insights từ Data Model."""

from unittest.mock import AsyncMock

import pytest
from main import app
from src.application.data_models.i_data_model_service import IDataModelService
from src.application.data_models.output import (
    DataModelDdlOutput,
    DataModelInsightOutput,
)
from src.presentation.dependencies.data_models import get_data_model_service


@pytest.mark.asyncio
async def test_get_data_model_ddl_contract(client) -> None:
    service = AsyncMock(spec=IDataModelService)
    service.generate_ddl.return_value = DataModelDdlOutput(
        ddl="CREATE TABLE users (id INT);",
        dialect="postgresql",
        revision=3,
    )
    app.dependency_overrides[get_data_model_service] = lambda: service
    try:
        response = await client.get("/api/v1/projects/86fd6b4e-1822-42db-a847-4d580abead3e/data-model/ddl")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["data"]["revision"] == 3


@pytest.mark.asyncio
async def test_get_data_model_insights_contract(client) -> None:
    service = AsyncMock(spec=IDataModelService)
    service.get_insights.return_value = [
        DataModelInsightOutput(
            id="users:grain",
            table_name="users",
            severity="info",
            title="Grain của bảng",
            description="Mỗi dòng là một user.",
        )
    ]
    app.dependency_overrides[get_data_model_service] = lambda: service
    try:
        response = await client.get("/api/v1/projects/86fd6b4e-1822-42db-a847-4d580abead3e/data-model/insights")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["data"][0]["table_name"] == "users"
