"""Integration test cho router Data Model (GET & PUT /api/v1/projects/{id}/data-model)."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from main import app
from src.application.data_models.i_data_model_service import IDataModelService
from src.application.data_models.input import (
    ChangeProposalIdInput,
    GenerateDataModelDdlInput,
    GetChangeProposalInput,
    GetDataModelInput,
    UpdateDataModelInput,
)
from src.application.data_models.output import (
    ChangeProposalDetailOutput,
    ChangeProposalSummaryOutput,
    DataModelDdlOutput,
    DataModelOutput,
)
from src.application.data_warehouse_workflows.output import ValidationIssue
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_model.entities import DataModel
from src.presentation.dependencies.data_models import get_data_model_service

API_PREFIX = "/api/v1"
SAMPLE_DBML = "Table users {\n  id uuid [pk]\n}"


def _output(project_id: UUID, revision: int = 1) -> DataModelOutput:
    """Dựng output Data Model tối thiểu cho test."""
    now = datetime.now(UTC)
    return DataModelOutput(
        id=uuid4(),
        project_id=project_id,
        dbml=SAMPLE_DBML,
        revision=revision,
        created_at=now,
        updated_at=now,
    )


class StubDataModelService(IDataModelService):
    """Service giả lập, ghi lại input nhận được để kiểm tra ánh xạ request."""

    def __init__(self, *, missing: bool = False) -> None:
        """Khởi tạo; `missing=True` để mô phỏng dự án chưa có Data Model."""
        self.missing = missing
        self.received: UpdateDataModelInput | None = None

    def _require_present(self, project_id: UUID) -> DataModelOutput:
        if self.missing:
            raise BusinessException(
                code=ErrorCode.DATA_MODEL_NOT_FOUND,
                message="Không tìm thấy Data Model của dự án.",
            )
        return _output(project_id)

    async def get_data_model(self, data: GetDataModelInput) -> DataModelOutput:
        return self._require_present(data.project_id)

    async def update_data_model(
        self, data: UpdateDataModelInput
    ) -> DataModelOutput:
        self.received = data
        model = DataModel(
            id=data.data_model_id,
            project_id=data.project_id,
            dbml=data.dbml,
            revision=data.base_revision + 1,
        )
        return DataModelOutput.from_domain(model)

    async def get_validation_issues(
        self, data: GetDataModelInput
    ) -> tuple[ValidationIssue, ...]:
        del data
        return ()

    async def get_change_proposal(
        self, data: GetChangeProposalInput
    ) -> ChangeProposalDetailOutput:
        raise NotImplementedError

    async def accept_change_proposal(self, data: ChangeProposalIdInput) -> DataModelOutput:
        raise NotImplementedError

    async def reject_change_proposal(
        self, data: ChangeProposalIdInput
    ) -> ChangeProposalSummaryOutput:
        raise NotImplementedError

    async def generate_ddl(
        self, data: GenerateDataModelDdlInput
    ) -> DataModelDdlOutput:
        return DataModelDdlOutput(
            ddl="CREATE TABLE users (id uuid PRIMARY KEY);",
            db_type=data.db_type,
            data_model_revision=1,
        )


async def _call(service: IDataModelService, method: str, url: str, **kwargs):
    """Gọi API với service đã được override, luôn dọn override sau khi xong."""
    app.dependency_overrides[get_data_model_service] = lambda: service
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            return await getattr(client, method)(url, **kwargs)
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_data_model_returns_success_envelope() -> None:
    """GET trả về snapshot DBML trong success envelope chuẩn."""
    project_id = uuid4()

    response = await _call(
        StubDataModelService(), "get", f"{API_PREFIX}/projects/{project_id}/data-model"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["project_id"] == str(project_id)
    assert body["data"]["dbml"] == SAMPLE_DBML


@pytest.mark.asyncio
async def test_get_data_model_returns_404_when_absent() -> None:
    """Dự án chưa có Data Model thì trả 404 kèm error_code ổn định."""
    response = await _call(
        StubDataModelService(missing=True),
        "get",
        f"{API_PREFIX}/projects/{uuid4()}/data-model",
    )

    assert response.status_code == 404
    assert response.json()["error_code"] == "DATA_MODEL_NOT_FOUND"


@pytest.mark.asyncio
async def test_generate_ddl_is_exposed_by_data_model_resource() -> None:
    """DDL được sinh qua Data Model API, không còn thuộc Sandbox resource."""
    project_id = uuid4()

    response = await _call(
        StubDataModelService(),
        "get",
        f"{API_PREFIX}/projects/{project_id}/data-model/ddl",
        params={"db_type": "POSTGRESQL"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["data_model_revision"] == 1


@pytest.mark.asyncio
async def test_update_data_model_maps_optimistic_locking_fields() -> None:
    """PUT chuyển đúng data_model_id và base_revision xuống application input."""
    service = StubDataModelService()
    project_id = uuid4()
    data_model_id = uuid4()

    response = await _call(
        service,
        "put",
        f"{API_PREFIX}/projects/{project_id}/data-model",
        json={
            "data_model_id": str(data_model_id),
            "dbml": SAMPLE_DBML,
            "base_revision": 4,
        },
    )

    assert response.status_code == 200
    assert service.received is not None
    assert service.received.data_model_id == data_model_id
    assert service.received.base_revision == 4
    assert response.json()["data"]["revision"] == 5


@pytest.mark.asyncio
async def test_update_data_model_rejects_first_save_without_revision() -> None:
    """Model đầu tiên chỉ được tạo qua Save & Analyze workflow."""
    service = StubDataModelService()

    response = await _call(
        service,
        "put",
        f"{API_PREFIX}/projects/{uuid4()}/data-model",
        json={"dbml": SAMPLE_DBML},
    )

    assert response.status_code == 422
    assert service.received is None


@pytest.mark.asyncio
async def test_update_data_model_rejects_empty_dbml() -> None:
    """DBML rỗng bị chặn tại HTTP shape boundary."""
    service = StubDataModelService()

    response = await _call(
        service,
        "put",
        f"{API_PREFIX}/projects/{uuid4()}/data-model",
        json={"dbml": ""},
    )

    assert response.status_code == 422
    assert service.received is None
