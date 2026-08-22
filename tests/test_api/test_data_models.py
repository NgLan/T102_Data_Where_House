"""API tests cho contract GET/PUT Data Model UC5.1.3."""

from typing import cast
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from main import app
from src.application.data_models.i_data_model_service import IDataModelService
from src.application.data_models.output import DataModelOutput
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_model.entities import DataModel
from src.presentation.dependencies.data_models import get_data_model_service


@pytest.mark.asyncio
async def test_get_current_data_model_contract(client) -> None:
    """GET trả success envelope cùng DBML và revision hiện tại."""
    data_model = DataModel(project_id=uuid4(), dbml="Table users { id uuid }", revision=3)
    service = AsyncMock(spec=IDataModelService)
    service.get_data_model.return_value = DataModelOutput.from_domain(data_model)
    app.dependency_overrides[get_data_model_service] = lambda: service

    response = await client.get(f"/api/v1/projects/{data_model.project_id}/data-model")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["data"]["revision"] == 3
    assert response.json()["data"]["id"] == str(data_model.id)


@pytest.mark.asyncio
async def test_update_current_data_model_contract(client) -> None:
    """PUT nhận data_model_id, DBML, base_revision và trả revision mới."""
    data_model = DataModel(project_id=uuid4(), dbml="Table users { id uuid }", revision=4)
    service = AsyncMock(spec=IDataModelService)
    service.update_data_model.return_value = DataModelOutput.from_domain(data_model)
    app.dependency_overrides[get_data_model_service] = lambda: service
    payload = {
        "data_model_id": str(data_model.id),
        "dbml": data_model.dbml,
        "base_revision": 3,
    }

    response = await client.put(f"/api/v1/projects/{data_model.project_id}/data-model", json=payload)

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["data"]["revision"] == 4
    assert response.json()["data"]["dbml"] == data_model.dbml
    service.update_data_model.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_current_data_model_returns_conflict(client) -> None:
    """PUT chuyển BusinessException revision thành standard HTTP 409 envelope."""
    project_id = uuid4()
    service = AsyncMock(spec=IDataModelService)
    service.update_data_model.side_effect = BusinessException(
        code=ErrorCode.DATA_MODEL_REVISION_CONFLICT,
        message="Data Model đã thay đổi.",
    )
    app.dependency_overrides[get_data_model_service] = lambda: service
    payload = {
        "data_model_id": str(uuid4()),
        "dbml": "Table users { id uuid }",
        "base_revision": 3,
    }

    response = await client.put(f"/api/v1/projects/{project_id}/data-model", json=payload)

    app.dependency_overrides.clear()
    assert response.status_code == 409
    assert response.json()["error_code"] == "DATA_MODEL_REVISION_CONFLICT"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {
            "data_model_id": str(uuid4()),
            "dbml": "   ",
            "base_revision": 1,
        },
        {
            "data_model_id": str(uuid4()),
            "dbml": "Table users { id uuid }",
            "base_revision": 0,
        },
        {
            "data_model_id": str(uuid4()),
            "dbml": "Table users { id uuid }",
            "base_revision": "1",
        },
        {
            "data_model_id": "not-a-uuid",
            "dbml": "Table users { id uuid }",
            "base_revision": 1,
        },
        {
            "data_model_id": str(uuid4()),
            "dbml": "Table users { id uuid }",
            "base_revision": 1,
            "unexpected": True,
        },
    ],
)
async def test_update_data_model_validates_request_before_service(client, payload: dict[str, object]) -> None:
    """Request DTO từ chối toàn bộ input sai trước application boundary."""
    project_id = uuid4()
    service = AsyncMock(spec=IDataModelService)
    app.dependency_overrides[get_data_model_service] = lambda: service

    response = await client.put(
        f"/api/v1/projects/{project_id}/data-model",
        json=payload,
    )

    app.dependency_overrides.clear()
    assert response.status_code == 422
    assert response.json()["error_code"] == "VALIDATION_ERROR"
    service.update_data_model.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_data_model_maps_dto_errors_to_field_details(client) -> None:
    """Custom DTO validator phải đi qua validation handler thay vì business handler."""
    project_id = uuid4()
    service = AsyncMock(spec=IDataModelService)
    app.dependency_overrides[get_data_model_service] = lambda: service

    response = await client.put(
        f"/api/v1/projects/{project_id}/data-model",
        json={
            "data_model_id": "not-a-uuid",
            "dbml": "   ",
            "base_revision": 0,
        },
    )

    app.dependency_overrides.clear()
    assert response.status_code == 422
    assert response.json()["error_code"] == "VALIDATION_ERROR"
    assert {detail["field"] for detail in response.json()["details"]} == {
        "data_model_id",
        "dbml",
        "base_revision",
    }
    service.update_data_model.assert_not_awaited()


def test_data_model_openapi_uses_stable_generated_contract() -> None:
    """OpenAPI phải mô tả envelope, operation ID và error DTO tập trung."""
    path = app.openapi()["paths"]["/api/v1/projects/{project_id}/data-model"]
    get_operation = path["get"]
    put_operation = path["put"]

    assert get_operation["operationId"] == "getDataModel"
    assert put_operation["operationId"] == "updateDataModel"
    assert _response_schema_ref(get_operation, "200").endswith("ApiResponse_DataModelResponse_")
    assert _response_schema_ref(put_operation, "200").endswith("ApiResponse_DataModelResponse_")
    assert _response_schema_ref(put_operation, "409").endswith("ApiErrorResponse")


def _response_schema_ref(operation: dict[str, object], status_code: str) -> str:
    """Lấy schema reference của một OpenAPI response để kiểm tra contract."""
    responses = _mapping(operation["responses"])
    response = _mapping(responses[status_code])
    content = _mapping(response["content"])
    media_type = _mapping(content["application/json"])
    schema = _mapping(media_type["schema"])
    reference = schema["$ref"]
    assert isinstance(reference, str)
    return reference


def _mapping(value: object) -> dict[str, object]:
    """Thu hẹp một OpenAPI JSON object thành mapping có type rõ ràng."""
    assert isinstance(value, dict)
    return cast(dict[str, object], value)
