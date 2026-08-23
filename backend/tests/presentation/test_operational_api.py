"""Operational route behavior without a live database."""

from unittest.mock import AsyncMock

import pytest
from src.application.health.models import DatabaseHealthOutput, HealthOutput, LlmHealthOutput
from src.presentation.api.operational import readiness_check, root_docs_redirect


@pytest.mark.asyncio
async def test_root_redirects_to_docs_with_307() -> None:
    response = await root_docs_redirect()

    assert response.status_code == 307
    assert response.headers["location"] == "/docs"


@pytest.mark.asyncio
async def test_readiness_returns_503_without_leaking_database_error() -> None:
    service = AsyncMock()
    service.check.return_value = HealthOutput(
        "degraded",
        "test",
        "1.0.0",
        DatabaseHealthOutput("unhealthy", 10.0),
        LlmHealthOutput("unconfigured", "google", "model"),
    )

    response = await readiness_check(service)

    assert response.status_code == 503
    assert b"Database dependency is not ready" in response.body
    assert b"exception" not in response.body.lower()
