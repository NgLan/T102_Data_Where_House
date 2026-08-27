from unittest.mock import AsyncMock

import pytest
from main import app
from src.application.health.i_health_service import IHealthService
from src.application.health.models import (
    DatabaseHealthOutput,
    HealthOutput,
    LlmHealthOutput,
)
from src.presentation.dependencies.health import get_health_service


@pytest.mark.asyncio
async def test_health(client):
    service = AsyncMock(spec=IHealthService)
    service.check.return_value = HealthOutput(
        "ok",
        "test",
        "test",
        DatabaseHealthOutput("healthy", 0.1),
        LlmHealthOutput("configured", "test", "test"),
    )
    app.dependency_overrides[get_health_service] = lambda: service
    response = await client.get("/health")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["status"] == "ok"


@pytest.mark.asyncio
async def test_unknown_route_returns_404(client):
    """Route không tồn tại phải trả 404 chứ không phải lỗi 500."""
    response = await client.get("/api/v1/khong-ton-tai")
    assert response.status_code == 404
