"""API contract tests cho validation issues của Data Model."""

from unittest.mock import AsyncMock

import pytest
from main import app
from src.application.data_models.i_data_model_service import IDataModelService
from src.application.data_warehouse_workflows.output import (
    ValidationIssue,
    ValidationIssueCode,
    ValidationSeverity,
)
from src.presentation.dependencies.data_models import get_data_model_service


@pytest.mark.asyncio
async def test_get_data_model_validation_issues_contract(client) -> None:
    service = AsyncMock(spec=IDataModelService)
    service.get_validation_issues.return_value = (
        ValidationIssue(
            code=ValidationIssueCode.TABLE_PRIMARY_KEY_MISSING,
            table_name="users",
            severity=ValidationSeverity.ERROR,
            title="Bảng chưa có primary key",
            description="Bảng phải có primary key để xác định grain.",
        ),
    )
    app.dependency_overrides[get_data_model_service] = lambda: service
    try:
        response = await client.get(
            "/api/v1/projects/86fd6b4e-1822-42db-a847-4d580abead3e/"
            "data-model/validation-issues"
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["data"][0]["table_name"] == "users"
    assert response.json()["data"][0]["code"] == "TABLE_PRIMARY_KEY_MISSING"
