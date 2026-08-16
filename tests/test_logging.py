"""Unit tests cho Centralized Logging System (src/common/logging)."""

import asyncio
import json
import logging

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from src.common.logging import (
    clear_logging_context,
    get_agent_name,
    get_correlation_id,
    get_logger,
    get_request_id,
    get_session_id,
    set_agent_name,
    set_correlation_id,
    set_request_id,
    set_session_id,
)
from src.common.logging.filters import ContextLogFilter, SensitiveDataFilter
from src.common.logging.formatters import ConsoleFormatter, JsonFormatter
from src.common.middleware import RequestIDMiddleware


def test_get_logger():
    """Test get_logger trả về Logger instance hợp lệ, giữ nguyên tên được truyền vào."""
    logger = get_logger("test.module")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test.module"


def test_logging_context_management():
    """Test get/set/clear cho contextvars."""
    set_request_id("req_123")
    set_correlation_id("corr_456")
    set_session_id("sess_789")
    set_agent_name("schema_agent")

    assert get_request_id() == "req_123"
    assert get_correlation_id() == "corr_456"
    assert get_session_id() == "sess_789"
    assert get_agent_name() == "schema_agent"

    clear_logging_context()

    assert get_request_id() is None
    assert get_correlation_id() is None
    assert get_session_id() is None
    assert get_agent_name() is None


@pytest.mark.asyncio
async def test_logging_context_async_isolation():
    """Test tính độc lập giữa các async task (context isolation)."""

    async def task_a():
        set_request_id("req_A")
        await asyncio.sleep(0.01)
        assert get_request_id() == "req_A"

    async def task_b():
        set_request_id("req_B")
        await asyncio.sleep(0.01)
        assert get_request_id() == "req_B"

    await asyncio.gather(task_a(), task_b())
    clear_logging_context()


def test_sensitive_data_filter():
    """Test SensitiveDataFilter ẩn các thông tin nhạy cảm."""
    s_filter = SensitiveDataFilter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Login failed password='super_secret_pwd_123' token=Bearer abcdef123456",
        args=(),
        exc_info=None,
    )

    result = s_filter.filter(record)
    assert result is True
    assert "super_secret_pwd_123" not in record.msg
    assert "***REDACTED***" in record.msg


def test_context_log_filter():
    """Test ContextLogFilter tự động gắn request_id và agent_name vào LogRecord."""
    c_filter = ContextLogFilter()
    set_request_id("req_context_test")
    set_agent_name("analyst_agent")

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    c_filter.filter(record)
    assert getattr(record, "request_id") == "req_context_test"
    assert getattr(record, "agent_name") == "analyst_agent"

    clear_logging_context()


def test_console_formatter():
    """Test ConsoleFormatter tạo log string hợp lệ."""
    formatter = ConsoleFormatter()
    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Hello Console Log",
        args=(),
        exc_info=None,
    )
    record.request_id = "req_999"
    record.agent_name = "test_agent"

    output = formatter.format(record)
    assert "INFO" in output
    assert "test.logger" in output
    assert "Hello Console Log" in output
    assert "[req_id=req_999]" in output
    assert "[agent=test_agent]" in output


def test_json_formatter():
    """Test JsonFormatter tạo JSON structured log hợp lệ."""
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test.json",
        level=logging.ERROR,
        pathname="test.py",
        lineno=20,
        msg="JSON Log Error",
        args=(),
        exc_info=None,
    )
    record.request_id = "req_json_1"
    record.session_id = "sess_json_1"

    output = formatter.format(record)
    parsed = json.loads(output)

    assert parsed["level"] == "ERROR"
    assert parsed["logger"] == "test.json"
    assert parsed["message"] == "JSON Log Error"
    assert parsed["request_id"] == "req_json_1"
    assert parsed["session_id"] == "sess_json_1"


@pytest.mark.asyncio
async def test_request_logging_middleware():
    """Test RequestLoggingMiddleware tạo X-Request-ID header và quản lý context."""
    app = FastAPI()
    app.add_middleware(RequestIDMiddleware)

    @app.get("/test-endpoint")
    async def sample_endpoint():
        return {"current_req_id": get_request_id()}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Request 1: Client không truyền X-Request-ID
        res1 = await client.get("/test-endpoint")
        assert res1.status_code == 200
        req_id1 = res1.headers.get("X-Request-ID")
        assert req_id1 is not None
        assert req_id1.startswith("req_") or len(req_id1) == 36
        assert res1.json()["current_req_id"] == req_id1

        # Request 2: Client truyền custom X-Request-ID
        custom_id = "custom_req_header_123"
        res2 = await client.get(
            "/test-endpoint", headers={"X-Request-ID": custom_id}
        )
        assert res2.status_code == 200
        assert res2.headers.get("X-Request-ID") == custom_id
        assert res2.json()["current_req_id"] == custom_id


def test_clean_architecture_logging_isolation():
    """Test Clean Architecture isolation: core logging files không import framework/infrastructure."""
    import src.common.logging.config as cfg_mod
    import src.common.logging.context as ctx_mod
    import src.common.logging.filters as flt_mod
    import src.common.logging.formatters as fmt_mod
    import src.common.logging.logger as lgr_mod

    forbidden_modules = ["fastapi", "sqlalchemy", "redis", "langchain", "langgraph"]

    for mod in [ctx_mod, flt_mod, fmt_mod, lgr_mod, cfg_mod]:
        code = open(mod.__file__, encoding="utf-8").read()
        for forbidden in forbidden_modules:
            assert f"import {forbidden}" not in code, f"Module {mod.__file__} violates Clean Architecture by importing {forbidden}"
            assert f"from {forbidden}" not in code, f"Module {mod.__file__} violates Clean Architecture by importing {forbidden}"
