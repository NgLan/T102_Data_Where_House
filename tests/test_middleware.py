"""Unit và Integration tests cho FastAPI Middleware Layer (tests/test_middleware.py)."""

import asyncio
from collections.abc import AsyncGenerator

import pytest
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from httpx import ASGITransport, AsyncClient
from src.common.exceptions import (
    BusinessException,
    ErrorCode,
    register_exception_handlers,
)
from src.common.logging import clear_logging_context, get_request_id, set_request_id
from src.common.middleware import (
    HTTPLoggingMiddleware,
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
    setup_cors_middleware,
)


class DummySettings:
    """Mock Settings cho Middleware testing."""

    cors_origins_list = ["http://localhost:3000"]
    cors_allow_credentials = True
    cors_allow_methods_list = ["GET", "POST", "OPTIONS"]
    cors_allow_headers_list = ["*"]
    security_headers_enabled = True
    security_hsts_enabled = False


@pytest.fixture
def test_app() -> FastAPI:
    """Khởi tạo FastAPI test app chứa đầy đủ Middleware stack."""
    app = FastAPI()

    # Đăng ký Middleware theo đúng thứ tự (Innermost -> Outermost)
    app.add_middleware(HTTPLoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)
    setup_cors_middleware(app, DummySettings())
    app.add_middleware(SecurityHeadersMiddleware, enable_hsts=False)

    register_exception_handlers(app)

    @app.get("/api/v1/test")
    async def sample_endpoint():
        return {"request_id": get_request_id(), "message": "success"}

    @app.get("/api/v1/error")
    async def error_endpoint():
        raise BusinessException(
            message="User not found",
            code=ErrorCode.USER_NOT_FOUND,
        )

    @app.get("/api/v1/stream")
    async def stream_endpoint():
        async def generator() -> AsyncGenerator[bytes, None]:
            yield b"chunk1"
            yield b"chunk2"

        return StreamingResponse(generator(), media_type="text/plain")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


@pytest.mark.asyncio
async def test_request_id_generation(test_app: FastAPI):
    """Test sinh mới Request ID khi client không truyền header."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/test")
        assert response.status_code == 200
        req_id = response.headers.get("X-Request-ID")
        assert req_id is not None
        assert len(req_id) > 10
        assert response.json()["request_id"] == req_id


@pytest.mark.asyncio
async def test_request_id_reuse(test_app: FastAPI):
    """Test reuse Request ID khi client truyền header hợp lệ."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        custom_id = "custom-uuid-1234-5678"
        response = await client.get(
            "/api/v1/test", headers={"X-Request-ID": custom_id}
        )
        assert response.status_code == 200
        assert response.headers.get("X-Request-ID") == custom_id
        assert response.json()["request_id"] == custom_id


@pytest.mark.asyncio
async def test_correlation_id_propagation(test_app: FastAPI):
    """Test X-Correlation-ID được trích xuất và trả lại trong response headers."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        corr_id = "corr-flow-999"
        response = await client.get(
            "/api/v1/test", headers={"X-Correlation-ID": corr_id}
        )
        assert response.status_code == 200
        assert response.headers.get("X-Correlation-ID") == corr_id


@pytest.mark.asyncio
async def test_malicious_request_id_sanitization(test_app: FastAPI):
    """Test loại bỏ Request ID độc hại chứa newline/control chars để chống Log Injection."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        malicious_id = "fake_id\nERROR malicious_log_injection"
        response = await client.get(
            "/api/v1/test", headers={"X-Request-ID": malicious_id}
        )
        assert response.status_code == 200
        assigned_id = response.headers.get("X-Request-ID")
        assert assigned_id is not None
        assert "fake_id" not in assigned_id
        assert "\n" not in assigned_id


@pytest.mark.asyncio
async def test_async_context_isolation(test_app: FastAPI):
    """Test tính cô lập Request ID giữa các request chạy đồng thời (concurrent isolation)."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:

        async def make_request(req_num: int):
            req_id = f"concurrent-req-{req_num}"
            res = await client.get(
                "/api/v1/test", headers={"X-Request-ID": req_id}
            )
            assert res.status_code == 200
            assert res.json()["request_id"] == req_id

        tasks = [make_request(i) for i in range(10)]
        await asyncio.gather(*tasks)


@pytest.mark.asyncio
async def test_exception_handling_integration(test_app: FastAPI):
    """Test Middleware không nuốt Exception và Global Exception Handler hoạt động đúng."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/error")
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == ErrorCode.USER_NOT_FOUND.value
        # Kiểm tra X-Request-ID vẫn tồn tại ngay cả khi có ngoại lệ
        assert response.headers.get("X-Request-ID") is not None


@pytest.mark.asyncio
async def test_security_headers(test_app: FastAPI):
    """Test SecurityHeadersMiddleware đính kèm đúng các HTTP headers an toàn."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/test")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert (
            response.headers.get("Referrer-Policy")
            == "strict-origin-when-cross-origin"
        )
        assert response.headers.get("X-XSS-Protection") is None


@pytest.mark.asyncio
async def test_hsts_header_can_be_enabled():
    """Test HSTS chỉ được phát khi cấu hình bật tường minh."""
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware, enable_hsts=True)

    @app.get("/")
    async def endpoint():
        return {"status": "ok"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        response = await client.get("/")

    assert response.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"


def test_cors_rejects_wildcard_with_credentials():
    """Test CORS fail fast với tổ hợp cấu hình không an toàn."""

    class InvalidCorsSettings(DummySettings):
        cors_origins_list = ["*"]
        cors_allow_credentials = True

    with pytest.raises(ValueError, match="wildcard origin"):
        setup_cors_middleware(FastAPI(), InvalidCorsSettings())


@pytest.mark.asyncio
async def test_request_context_restores_outer_value(test_app: FastAPI):
    """Test middleware khôi phục ContextVar thay vì xóa context bao ngoài."""
    set_request_id("outer-request")
    try:
        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/test", headers={"X-Request-ID": "inner-request"}
            )
        assert response.json()["request_id"] == "inner-request"
        assert get_request_id() == "outer-request"
    finally:
        clear_logging_context()


@pytest.mark.asyncio
async def test_cors_middleware(test_app: FastAPI):
    """Test CORS Middleware phản hồi đúng theo Origin Header."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        # Allowed origin
        res = await client.get(
            "/api/v1/test", headers={"Origin": "http://localhost:3000"}
        )
        assert (
            res.headers.get("Access-Control-Allow-Origin")
            == "http://localhost:3000"
        )

        # Disallowed origin
        res_disallowed = await client.get(
            "/api/v1/test", headers={"Origin": "http://malicious-site.com"}
        )
        assert "Access-Control-Allow-Origin" not in res_disallowed.headers


@pytest.mark.asyncio
async def test_streaming_response_compatibility(test_app: FastAPI):
    """Test Middleware tương thích hoàn hảo với StreamingResponse mà không làm vỡ stream."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/stream")
        assert response.status_code == 200
        assert response.text == "chunk1chunk2"
        assert response.headers.get("X-Request-ID") is not None
