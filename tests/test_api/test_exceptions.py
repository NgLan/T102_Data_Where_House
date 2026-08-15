"""Tests cho hệ thống Exception Handling toàn cục."""

from http import HTTPStatus

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.error_status import ERROR_STATUS_MAP, get_http_status_code
from src.common.exceptions.handler import register_exception_handlers
from src.common.exceptions.system import SystemException


# Tạo app FastAPI phục vụ riêng cho thử nghiệm exception handling
def create_test_app() -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/test/business-not-found")
    async def route_business_not_found():
        raise BusinessException(
            code=ErrorCode.USER_NOT_FOUND,
            message="User not found.",
        )

    @app.get("/test/business-conflict")
    async def route_business_conflict():
        raise BusinessException(
            code=ErrorCode.REVISION_CONFLICT,
            message="The current revision is outdated.",
            details={"current_revision": 2, "provided_revision": 1},
        )

    @app.get("/test/system-db-error")
    async def route_system_db_error():
        raise SystemException(
            code=ErrorCode.DATABASE_ERROR,
            message="Database operation failed.",
        )

    @app.get("/test/system-llm-error")
    async def route_system_llm_error():
        raise SystemException(
            code=ErrorCode.LLM_ERROR,
            message="LLM service is unavailable.",
        )

    class DummyPayload(BaseModel):
        age: int
        name: str

    @app.post("/test/validation")
    async def route_validation(payload: DummyPayload):
        return {"status": "ok"}

    @app.get("/test/unexpected-error")
    async def route_unexpected_error():
        raise RuntimeError("Secret DB password or internal crash trace")

    return app


@pytest_asyncio.fixture
async def test_client():
    test_app = create_test_app()
    transport = ASGITransport(app=test_app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_business_exception_not_found(test_client: AsyncClient):
    response = await test_client.get("/test/business-not-found")
    assert response.status_code == HTTPStatus.NOT_FOUND
    data = response.json()
    assert data["code"] == 404
    assert data["error_code"] == "USER_NOT_FOUND"
    assert data["message"] == "User not found."
    assert data["details"] is None


@pytest.mark.asyncio
async def test_business_exception_conflict(test_client: AsyncClient):
    response = await test_client.get("/test/business-conflict")
    assert response.status_code == HTTPStatus.CONFLICT
    data = response.json()
    assert data["code"] == 409
    assert data["error_code"] == "REVISION_CONFLICT"
    assert data["message"] == "The current revision is outdated."
    assert data["details"] == {"current_revision": 2, "provided_revision": 1}


@pytest.mark.asyncio
async def test_system_exception_db_error(test_client: AsyncClient):
    response = await test_client.get("/test/system-db-error")
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    data = response.json()
    assert data["code"] == 500
    assert data["error_code"] == "DATABASE_ERROR"
    assert data["message"] == "Database operation failed."


@pytest.mark.asyncio
async def test_system_exception_llm_error(test_client: AsyncClient):
    response = await test_client.get("/test/system-llm-error")
    assert response.status_code == HTTPStatus.BAD_GATEWAY
    data = response.json()
    assert data["code"] == 502
    assert data["error_code"] == "LLM_ERROR"
    assert data["message"] == "LLM service is unavailable."


@pytest.mark.asyncio
async def test_validation_error_format(test_client: AsyncClient):
    # Gửi hai field sai để bảo đảm mỗi lỗi có một phần tử details riêng.
    response = await test_client.post("/test/validation", json={"age": "not-an-int"})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    data = response.json()
    assert data["code"] == 422
    assert data["error_code"] == "VALIDATION_ERROR"
    assert data["message"] == "Request validation failed."
    assert {detail["field"] for detail in data["details"]} == {"age", "name"}
    assert all(set(detail) == {"field", "message"} and detail["message"] for detail in data["details"])


@pytest.mark.asyncio
async def test_unhandled_unexpected_exception(test_client: AsyncClient):
    response = await test_client.get("/test/unexpected-error")
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    data = response.json()
    assert data["code"] == 500
    assert data["error_code"] == "INTERNAL_SERVER_ERROR"
    assert data["message"] == "Internal server error."
    # Kiểm tra không rò rỉ secret / stack trace ở response
    assert "Secret DB password" not in response.text


def test_all_error_codes_are_mapped():
    """Đảm bảo mọi ErrorCode định nghĩa trong ErrorCode Enum đều được ánh xá trong ERROR_STATUS_MAP."""
    for error_code in ErrorCode:
        assert error_code in ERROR_STATUS_MAP, f"ErrorCode {error_code} chưa được định nghĩa trong ERROR_STATUS_MAP!"
        status = get_http_status_code(error_code)
        assert isinstance(status, HTTPStatus)
