"""Unit tests cho LoggingInterceptor (test_logging.py)."""

import logging

import pytest
from src.common.exceptions.base import AppException
from src.common.exceptions.error_codes import ErrorCode
from src.common.interceptors.context import InterceptorContext
from src.common.interceptors.logging import LoggingInterceptor


@pytest.mark.asyncio
async def test_logging_interceptor_success(caplog: pytest.LogCaptureFixture) -> None:
    """Kiểm tra LoggingInterceptor ghi log khi operation thành công."""
    caplog.set_level(logging.INFO)
    interceptor = LoggingInterceptor()
    context = InterceptorContext.create("CreateProjectUseCase", request_id="req_123")
    context.metadata["duration_ms"] = 45.67

    async def target_op() -> str:
        return "project_id_1"

    result = await interceptor.intercept(context, target_op)

    assert result == "project_id_1"
    assert "Bắt đầu thực thi operation 'CreateProjectUseCase'" in caplog.text
    assert "Hoàn tất operation 'CreateProjectUseCase' trong 45.67ms" in caplog.text


@pytest.mark.asyncio
async def test_logging_interceptor_app_exception(caplog: pytest.LogCaptureFixture) -> None:
    """Kiểm tra LoggingInterceptor log WARNING và re-raise cho AppException."""
    caplog.set_level(logging.WARNING)
    interceptor = LoggingInterceptor()
    context = InterceptorContext.create("UpdateRequirementUseCase", request_id="req_456")

    async def target_failing() -> None:
        raise AppException(code=ErrorCode.VALIDATION_ERROR, message="Invalid requirement")

    with pytest.raises(AppException) as exc_info:
        await interceptor.intercept(context, target_failing)

    assert exc_info.value.code == ErrorCode.VALIDATION_ERROR
    assert "Thất bại operation 'UpdateRequirementUseCase': [VALIDATION_ERROR] Invalid requirement" in caplog.text
    # Kiểm tra log record có chứa event và error_code extra
    matching_records = [r for r in caplog.records if getattr(r, "event", None) == "application_operation_failed"]
    assert len(matching_records) == 1
    assert getattr(matching_records[0], "error_code") == "VALIDATION_ERROR"
