import pytest


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["status"] == "ok"


@pytest.mark.asyncio
async def test_unknown_route_returns_404(client):
    """Route không tồn tại phải trả 404 chứ không phải lỗi 500."""
    response = await client.get("/api/v1/khong-ton-tai")
    assert response.status_code == 404
