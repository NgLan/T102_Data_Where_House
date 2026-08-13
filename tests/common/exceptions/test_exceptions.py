"""Unit tests kiểm tra toàn bộ Hệ thống xử lý Exception và các Exception Handling Principles."""

from http import HTTPStatus
from typing import Any

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from src.common.exceptions import (
    AppException,
    BusinessException,
    ErrorCode,
    InfrastructureException,
    SystemException,
    register_exception_handlers,
)


class RawThirdPartyError(Exception):
    """Mô phỏng lỗi từ thư viện bên thứ 3 (SQLAlchemy, Redis, OpenAI...)."""

    pass


def test_exception_class_hierarchy() -> None:
    """Kiểm tra quan hệ kế thừa của các Exception classes."""
    infra_exc = InfrastructureException(
        code=ErrorCode.DATABASE_ERROR,
        message="Database connection failed.",
    )
    assert isinstance(infra_exc, SystemException)
    assert isinstance(infra_exc, AppException)
    assert isinstance(infra_exc, Exception)

    biz_exc = BusinessException(
        code=ErrorCode.USER_NOT_FOUND,
        message="User not found.",
    )
    assert isinstance(biz_exc, AppException)
    assert not isinstance(biz_exc, SystemException)


def test_business_exception_standard_usage() -> None:
    """Kiểm tra BusinessException sử dụng ErrorCode chuẩn mà không cần tạo class con riêng."""
    exc = BusinessException(
        code=ErrorCode.REVISION_CONFLICT,
        message="Requirement version conflict.",
        details={"version": 2},
    )
    assert exc.code == ErrorCode.REVISION_CONFLICT
    assert exc.message == "Requirement version conflict."
    assert exc.details == {"version": 2}
    assert "[REVISION_CONFLICT] Requirement version conflict." in str(exc)


def test_infrastructure_exception_chaining() -> None:
    """Kiểm tra nguyên tắc exception chaining bằng `raise ... from exc` để bảo toàn __cause__."""
    raw_cause = RawThirdPartyError("Connection timed out to Postgres DB")

    try:
        try:
            raise raw_cause
        except RawThirdPartyError as exc:
            raise InfrastructureException(
                code=ErrorCode.DATABASE_ERROR,
                message="Failed to execute database query.",
            ) from exc
    except InfrastructureException as caught:
        assert caught.__cause__ is raw_cause
        assert isinstance(caught.__cause__, RawThirdPartyError)
        assert str(caught.__cause__) == "Connection timed out to Postgres DB"


def test_no_silent_exception_hiding() -> None:
    """Kiểm tra nguyên tắc không nuốt lỗi (exception propagation)."""

    def failing_repository_call() -> None:
        raise RawThirdPartyError("DB Disk Full")

    def service_layer() -> Any:
        try:
            failing_repository_call()
        except RawThirdPartyError as exc:
            # Chuyển đổi exception đúng chuẩn thay vì trả về None hay []
            raise InfrastructureException(
                code=ErrorCode.DATABASE_ERROR,
                message="Infrastructure storage failed.",
            ) from exc

    with pytest.raises(InfrastructureException) as exc_info:
        service_layer()

    assert exc_info.value.code == ErrorCode.DATABASE_ERROR
    assert exc_info.value.__cause__ is not None
    assert isinstance(exc_info.value.__cause__, RawThirdPartyError)


def test_business_exception_conversion_with_justification() -> None:
    """Kiểm tra chuyển đổi technical exception thành BusinessException khi có căn cứ nghiệp vụ rõ ràng.

    Ví dụ: Lỗi Unique Constraint Violation từ DB (IntegrityError) khi đăng ký trùng Email -> BusinessException(USER_ALREADY_EXISTS).
    """
    raw_db_unique_err = RawThirdPartyError("duplicate key value violates unique constraint 'users_email_key'")

    try:
        try:
            raise raw_db_unique_err
        except RawThirdPartyError as exc:
            # Có căn cứ nghiệp vụ rõ ràng: Trùng email
            raise BusinessException(
                code=ErrorCode.USER_NOT_FOUND,
                message="Email address is already in use.",
            ) from exc
    except BusinessException as caught:
        assert caught.code == ErrorCode.USER_NOT_FOUND
        assert caught.__cause__ is raw_db_unique_err


# --- Integration tests với FastAPI Global Exception Handler ---

def create_exception_test_app() -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/test/infra-db-exception")
    async def route_infra_db_exception():
        try:
            raise RawThirdPartyError("Postgres connection lost")
        except RawThirdPartyError as exc:
            raise InfrastructureException(
                code=ErrorCode.DATABASE_ERROR,
                message="Database connection error.",
            ) from exc

    @app.get("/test/infra-external-exception")
    async def route_infra_external_exception():
        try:
            raise RawThirdPartyError("Redis cluster unreachable")
        except RawThirdPartyError as exc:
            raise InfrastructureException(
                code=ErrorCode.EXTERNAL_SERVICE_ERROR,
                message="Cache infrastructure is unavailable.",
            ) from exc

    return app


@pytest_asyncio.fixture
async def test_client():
    app = create_exception_test_app()
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_global_handler_processes_infrastructure_exception_500(test_client: AsyncClient):
    """Kiểm tra Global Exception Handler xử lý InfrastructureException(DATABASE_ERROR) thành 500 JSONResponse."""
    response = await test_client.get("/test/infra-db-exception")
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    data = response.json()
    assert data["code"] == 500
    assert data["error_code"] == "DATABASE_ERROR"
    assert data["message"] == "Database connection error."
    # Bảo mật: không làm rò rỉ raw exception string ở HTTP response
    assert "Postgres connection lost" not in response.text


@pytest.mark.asyncio
async def test_global_handler_processes_infrastructure_exception_502(test_client: AsyncClient):
    """Kiểm tra Global Exception Handler xử lý InfrastructureException(EXTERNAL_SERVICE_ERROR) thành 502 JSONResponse."""
    response = await test_client.get("/test/infra-external-exception")
    assert response.status_code == HTTPStatus.BAD_GATEWAY
    data = response.json()
    assert data["code"] == 502
    assert data["error_code"] == "EXTERNAL_SERVICE_ERROR"
    assert data["message"] == "Cache infrastructure is unavailable."
    # Bảo mật: không làm rò rỉ raw exception string ở HTTP response
    assert "Redis cluster unreachable" not in response.text
