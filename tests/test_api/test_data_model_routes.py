"""Kiểm thử API endpoints Mô hình Dữ liệu & Đề xuất Thay đổi (T-030, T-031, T-024, T-032, T-033)."""

from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from main import app
from src.domain.data_model.entities import DataModel, DataModelChange
from src.domain.project.entities import Project
from src.presentation.dependencies.application import (
    get_data_model_change_repository,
    get_data_model_repository,
    get_data_model_reviser,
    get_project_repository,
    get_unit_of_work,
)

from tests.test_application.test_ai_revision_use_cases import (
    FakeProjectRepository,
    FakeReviser,
    FakeUnitOfWork,
)
from tests.test_application.test_data_model_use_cases import (
    PROPOSED_DBML,
    SAMPLE_DBML,
    FakeChangeRepository,
    FakeDataModelRepository,
)

API_PREFIX = "/api/v1"


@pytest.fixture
def seeded_project() -> Project:
    """Dự án mẫu sở hữu mô hình dữ liệu dùng trong kiểm thử."""
    return Project(name="Demo", requirement="Thiết kế DWH gọi xe.", user_id=uuid4())


@pytest.fixture
def seeded_data_model(seeded_project: Project) -> DataModel:
    """Mô hình dữ liệu mẫu ở revision 3 dùng cho toàn bộ bài kiểm thử API."""
    return DataModel(project_id=seeded_project.id, dbml=SAMPLE_DBML, revision=3)


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
    seeded_data_model: DataModel,
    seeded_change: DataModelChange,
    seeded_project: Project,
) -> AsyncGenerator[AsyncClient, None]:
    """HTTP client với repository, AI Agent và giao dịch đều được thay bằng bản giả lập."""
    app.dependency_overrides[get_data_model_repository] = lambda: FakeDataModelRepository(
        [seeded_data_model]
    )
    app.dependency_overrides[get_data_model_change_repository] = lambda: FakeChangeRepository(
        [seeded_change]
    )
    app.dependency_overrides[get_project_repository] = lambda: FakeProjectRepository(
        [seeded_project]
    )
    app.dependency_overrides[get_data_model_reviser] = lambda: FakeReviser()
    app.dependency_overrides[get_unit_of_work] = lambda: FakeUnitOfWork()
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


# --- POST /data-models/{id}/ai-revisions (T-024) ------------------------------


@pytest.mark.asyncio
async def test_ai_revision_creates_proposal(
    api_client: AsyncClient, seeded_data_model: DataModel, seeded_project: Project
) -> None:
    """AI tạo đề xuất mới ở trạng thái PROPOSED, base_revision khớp revision hiện tại."""
    response = await api_client.post(
        f"{API_PREFIX}/data-models/{seeded_data_model.id}/ai-revisions",
        json={"instruction": "tách Dim_Driver thành Dim_Driver và Dim_Vehicle"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "PROPOSED"
    assert data["proposed_dbml"] == PROPOSED_DBML
    assert data["current_dbml"] == SAMPLE_DBML
    assert data["base_revision"] == 3
    assert data["current_revision"] == 3
    assert data["is_outdated"] is False
    assert data["user_id"] == str(seeded_project.user_id)
    assert data["summary"] == "Đã thêm cột rating."


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "instruction",
    ["", "abc", "x" * 2001],
    ids=["empty", "too_short", "too_long"],
)
async def test_ai_revision_rejects_invalid_instruction(
    api_client: AsyncClient, seeded_data_model: DataModel, instruction: str
) -> None:
    """Câu lệnh rỗng, quá ngắn hoặc quá dài bị chặn ngay ở tầng validate."""
    response = await api_client.post(
        f"{API_PREFIX}/data-models/{seeded_data_model.id}/ai-revisions",
        json={"instruction": instruction},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ai_revision_returns_404_for_unknown_data_model(
    api_client: AsyncClient,
) -> None:
    """Chỉnh sửa mô hình không tồn tại trả về 404."""
    response = await api_client.post(
        f"{API_PREFIX}/data-models/{uuid4()}/ai-revisions",
        json={"instruction": "thêm cột rating vào Dim_Driver"},
    )

    assert response.status_code == 404
    assert response.json()["error_code"] == "DATA_MODEL_NOT_FOUND"


# --- POST /data-model-changes/{id}/accept (T-032) -----------------------------


@pytest.mark.asyncio
async def test_accept_applies_proposal_and_returns_new_data_model(
    api_client: AsyncClient, seeded_change: DataModelChange
) -> None:
    """Chấp nhận thành công trả về mô hình đã áp dụng DBML mới và tăng revision."""
    response = await api_client.post(
        f"{API_PREFIX}/data-model-changes/{seeded_change.id}/accept"
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["dbml"] == PROPOSED_DBML
    assert data["revision"] == 4


@pytest.mark.asyncio
async def test_accept_twice_returns_422(
    api_client: AsyncClient, seeded_change: DataModelChange
) -> None:
    """Chấp nhận lại một đề xuất đã ACCEPTED phải bị từ chối với mã 422."""
    first = await api_client.post(
        f"{API_PREFIX}/data-model-changes/{seeded_change.id}/accept"
    )
    assert first.status_code == 200

    second = await api_client.post(
        f"{API_PREFIX}/data-model-changes/{seeded_change.id}/accept"
    )

    assert second.status_code == 422
    assert second.json()["error_code"] == "INVALID_PROPOSAL_STATUS_TRANSITION"


@pytest.mark.asyncio
async def test_accept_outdated_proposal_returns_409(
    seeded_data_model: DataModel, seeded_project: Project
) -> None:
    """Đề xuất dựa trên revision cũ trả về 409 và được đánh dấu CONFLICTED."""
    outdated = DataModelChange(
        data_model_id=seeded_data_model.id, base_revision=1, proposed_dbml=PROPOSED_DBML
    )
    app.dependency_overrides[get_data_model_repository] = lambda: FakeDataModelRepository(
        [seeded_data_model]
    )
    app.dependency_overrides[get_data_model_change_repository] = lambda: FakeChangeRepository(
        [outdated]
    )
    app.dependency_overrides[get_project_repository] = lambda: FakeProjectRepository(
        [seeded_project]
    )
    app.dependency_overrides[get_unit_of_work] = lambda: FakeUnitOfWork()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            f"{API_PREFIX}/data-model-changes/{outdated.id}/accept"
        )
    app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json()["error_code"] == "REVISION_CONFLICT"
    assert outdated.status.value == "CONFLICTED"
    assert seeded_data_model.revision == 3


@pytest.mark.asyncio
async def test_accept_returns_404_when_proposal_absent(
    api_client: AsyncClient,
) -> None:
    """Chấp nhận đề xuất không tồn tại trả về 404."""
    response = await api_client.post(
        f"{API_PREFIX}/data-model-changes/{uuid4()}/accept"
    )

    assert response.status_code == 404
    assert response.json()["error_code"] == "PROPOSAL_NOT_FOUND"


# --- POST /data-model-changes/{id}/reject (T-033) -----------------------------


@pytest.mark.asyncio
async def test_reject_marks_proposal_rejected(
    api_client: AsyncClient, seeded_change: DataModelChange, seeded_data_model: DataModel
) -> None:
    """Từ chối thành công đổi trạng thái đề xuất mà không đụng tới mô hình dữ liệu."""
    response = await api_client.post(
        f"{API_PREFIX}/data-model-changes/{seeded_change.id}/reject"
    )

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "REJECTED"
    assert seeded_data_model.dbml == SAMPLE_DBML
    assert seeded_data_model.revision == 3


@pytest.mark.asyncio
async def test_reject_twice_returns_422(
    api_client: AsyncClient, seeded_change: DataModelChange
) -> None:
    """Từ chối lại một đề xuất đã REJECTED phải bị từ chối với mã 422."""
    first = await api_client.post(
        f"{API_PREFIX}/data-model-changes/{seeded_change.id}/reject"
    )
    assert first.status_code == 200

    second = await api_client.post(
        f"{API_PREFIX}/data-model-changes/{seeded_change.id}/reject"
    )

    assert second.status_code == 422
    assert second.json()["error_code"] == "INVALID_PROPOSAL_STATUS_TRANSITION"


@pytest.mark.asyncio
async def test_reject_returns_404_when_proposal_absent(
    api_client: AsyncClient,
) -> None:
    """Từ chối đề xuất không tồn tại trả về 404."""
    response = await api_client.post(
        f"{API_PREFIX}/data-model-changes/{uuid4()}/reject"
    )

    assert response.status_code == 404
    assert response.json()["error_code"] == "PROPOSAL_NOT_FOUND"
