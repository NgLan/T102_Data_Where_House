"""API contract tests cho project analysis status và action."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from main import app
from src.application.data_warehouse_workflows.i_data_warehouse_workflow_service import (
    IDataWarehouseWorkflowService,
)
from src.application.data_warehouse_workflows.output import (
    AnalysisStatusOutput,
    InputReadinessStatus,
    RecommendedWorkflowAction,
)
from src.presentation.dependencies.data_warehouse_workflows import get_data_warehouse_workflow


def _status() -> AnalysisStatusOutput:
    """Tạo outdated status đại diện cho Project đã có model."""
    return AnalysisStatusOutput(
        False,
        True,
        True,
        True,
        0,
        RecommendedWorkflowAction.ANALYZE_CHANGES,
        InputReadinessStatus.SOURCE_DATA_REQUIRED,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["get", "post"])
async def test_project_analysis_contract(client, method: str) -> None:
    """GET chỉ đọc và POST gọi đúng workflow operation với typed response."""
    service = AsyncMock(spec=IDataWarehouseWorkflowService)
    service.get_analysis_status.return_value = _status()
    service.reanalyze.return_value = _status()
    app.dependency_overrides[get_data_warehouse_workflow] = lambda: service

    suffix = "analysis-status" if method == "get" else "reanalyze"
    response = await getattr(client, method)(f"/api/v1/projects/{uuid4()}/{suffix}")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["data"]["data_model_exists"] is True
    assert response.json()["data"]["recommended_action"] == "ANALYZE_CHANGES"
    operation = service.get_analysis_status if method == "get" else service.reanalyze
    operation.assert_awaited_once()
