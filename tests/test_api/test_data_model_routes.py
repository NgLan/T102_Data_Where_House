"""Kiểm thử API endpoints Mô hình Dữ liệu & Đề xuất Thay đổi (T-030, T-031)."""

from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from main import app
from src.domain.data_model.entities import DataModel, DataModelChange
from src.presentation.dependencies.application import (
    get_data_model_change_repository,
    get_data_model_repository,
)

from tests.test_application.test_data_model_use_cases import (
    PROPOSED_DBML,
    SAMPLE_DBML,
    FakeChangeRepository,
    FakeDataModelRepository,
)

API_PREFIX = "/api/v1"


@pytest.fixture
def seeded_data_model() -> DataModel:
    """Mô hình dữ liệu mẫu ở revision 3 dùng cho toàn bộ bài kiểm thử API."""
    return DataModel(project_id=uuid4(), dbml=SAMPLE_DBML, revision=3)


@pytest.fixture
def seeded_change(seeded_data_model: DataModel) -> DataModelChange:
    """Đề xuất thay đổi đang chờ duyệt, cùng base_revision với mô hình dữ liệu."""
    return DataModelChange(
        data_model_id=seeded_data_model.id,
        base_revision=3,
        proposed_dbml=PROPOSED_DBML,
    )


@pytest_asyncio.fixture
async def api_client(
    seeded_data_model: DataModel, seeded_change: DataModelChange
) -> AsyncGenerator[AsyncClient, None]:
    """HTTP client với repository được thay bằng bản giả lập trong bộ nhớ."""
    app.dependency_overrides[get_data_model_repository] = lambda: FakeDataModelRepository(
        [seeded_data_model]
    )
    app.dependency_overrides[get_data_model_change_repository] = lambda: FakeChangeRepository(
        [seeded_change]
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


# --- GET /projects/{project_id}/data-model ------------------------------------


@pytest.mark.asyncio
async def test_get_project_data_model_returns_success_envelope(
    api_client: AsyncClient, seeded_data_model: DataModel
) -> None:
    """Trả về mô hình dữ liệu trong khung phản hồi chuẩn của hệ thống."""
    response = await api_client.get(
        f"{API_PREFIX}/projects/{seeded_data_model.project_id}/data-model"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["code"] == 200
    assert body["data"]["dbml"] == SAMPLE_DBML
    assert body["data"]["revision"] == 3


@pytest.mark.asyncio
async def test_get_project_data_model_returns_404_when_absent(
    api_client: AsyncClient,
) -> None:
    """Dự án chưa có mô hình dữ liệu trả về 404 kèm error_code chuẩn."""
    response = await api_client.get(f"{API_PREFIX}/projects/{uuid4()}/data-model")

    assert response.status_code == 404
    assert response.json()["error_code"] == "DATA_MODEL_NOT_FOUND"


# --- GET /data-models/{id}/ddl (T-030) ----------------------------------------


@pytest.mark.asyncio
async def test_generate_ddl_defaults_to_postgresql(
    api_client: AsyncClient, seeded_data_model: DataModel
) -> None:
    """Không truyền `dialect` thì mặc định sinh DDL cho PostgreSQL."""
    response = await api_client.get(f"{API_PREFIX}/data-models/{seeded_data_model.id}/ddl")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["dialect"] == "postgresql"
    assert data["schema_name"] == "sandbox_dwh"
    assert data["table_count"] == 1
    assert "CREATE TABLE IF NOT EXISTS sandbox_dwh." in data["ddl"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("dialect", "expected_marker"),
    [
        ("postgresql", "CREATE TABLE IF NOT EXISTS"),
        ("snowflake", "CREATE OR REPLACE TABLE"),
        ("bigquery", "NOT ENFORCED"),
    ],
)
async def test_generate_ddl_supports_all_dialects(
    api_client: AsyncClient,
    seeded_data_model: DataModel,
    dialect: str,
    expected_marker: str,
) -> None:
    """Người dùng chọn được cả ba hệ quản trị CSDL và nhận đúng cú pháp tương ứng."""
    response = await api_client.get(
        f"{API_PREFIX}/data-models/{seeded_data_model.id}/ddl",
        params={"dialect": dialect},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["dialect"] == dialect
    assert expected_marker in data["ddl"]


@pytest.mark.asyncio
async def test_generate_ddl_accepts_custom_schema_name(
    api_client: AsyncClient, seeded_data_model: DataModel
) -> None:
    """Cho phép ghi đè tên schema Sandbox qua query param."""
    response = await api_client.get(
        f"{API_PREFIX}/data-models/{seeded_data_model.id}/ddl",
        params={"schema_name": "sandbox_demo"},
    )

    data = response.json()["data"]
    assert data["schema_name"] == "sandbox_demo"
    assert "sandbox_demo" in data["ddl"]


@pytest.mark.asyncio
async def test_generate_ddl_rejects_unknown_dialect(
    api_client: AsyncClient, seeded_data_model: DataModel
) -> None:
    """Dialect không nằm trong danh sách hỗ trợ bị từ chối ở tầng validate."""
    response = await api_client.get(
        f"{API_PREFIX}/data-models/{seeded_data_model.id}/ddl",
        params={"dialect": "oracle"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_generate_ddl_returns_404_for_unknown_data_model(
    api_client: AsyncClient,
) -> None:
    """Sinh DDL cho mô hình không tồn tại trả về 404 kèm error_code chuẩn."""
    response = await api_client.get(f"{API_PREFIX}/data-models/{uuid4()}/ddl")

    assert response.status_code == 404
    assert response.json()["error_code"] == "DATA_MODEL_NOT_FOUND"


# --- GET /data-models/{id}/changes (T-031) ------------------------------------


@pytest.mark.asyncio
async def test_list_changes_returns_proposals(
    api_client: AsyncClient, seeded_data_model: DataModel, seeded_change: DataModelChange
) -> None:
    """Trả về danh sách đề xuất thay đổi của mô hình dữ liệu."""
    response = await api_client.get(
        f"{API_PREFIX}/data-models/{seeded_data_model.id}/changes"
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["id"] == str(seeded_change.id)
    assert data[0]["status"] == "PROPOSED"
    assert data[0]["base_revision"] == 3


@pytest.mark.asyncio
async def test_list_changes_filters_by_status(
    api_client: AsyncClient, seeded_data_model: DataModel
) -> None:
    """Lọc theo trạng thái loại bỏ các đề xuất không khớp."""
    response = await api_client.get(
        f"{API_PREFIX}/data-models/{seeded_data_model.id}/changes",
        params={"status": "ACCEPTED"},
    )

    assert response.status_code == 200
    assert response.json()["data"] == []


# --- GET /data-model-changes/{id} (T-031) -------------------------------------


@pytest.mark.asyncio
async def test_get_change_proposal_returns_both_dbml_and_revisions(
    api_client: AsyncClient, seeded_change: DataModelChange
) -> None:
    """UC6.1: một lần gọi trả đủ DBML đề xuất, DBML hiện hành và base revision."""
    response = await api_client.get(f"{API_PREFIX}/data-model-changes/{seeded_change.id}")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["proposed_dbml"] == PROPOSED_DBML
    assert data["current_dbml"] == SAMPLE_DBML
    assert data["base_revision"] == 3
    assert data["current_revision"] == 3
    assert data["is_outdated"] is False


@pytest.mark.asyncio
async def test_get_change_proposal_flags_outdated_proposal(
    seeded_data_model: DataModel,
) -> None:
    """Đề xuất dựa trên revision cũ phải được đánh dấu lỗi thời để cảnh báo người dùng."""
    outdated = DataModelChange(
        data_model_id=seeded_data_model.id, base_revision=1, proposed_dbml=PROPOSED_DBML
    )
    app.dependency_overrides[get_data_model_repository] = lambda: FakeDataModelRepository(
        [seeded_data_model]
    )
    app.dependency_overrides[get_data_model_change_repository] = lambda: FakeChangeRepository(
        [outdated]
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"{API_PREFIX}/data-model-changes/{outdated.id}")
    app.dependency_overrides.clear()

    data = response.json()["data"]
    assert data["is_outdated"] is True
    assert data["base_revision"] == 1
    assert data["current_revision"] == 3


@pytest.mark.asyncio
async def test_get_change_proposal_returns_404_when_absent(
    api_client: AsyncClient,
) -> None:
    """Đề xuất không tồn tại trả về 404 kèm error_code chuẩn."""
    response = await api_client.get(f"{API_PREFIX}/data-model-changes/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["error_code"] == "PROPOSAL_NOT_FOUND"
