"""Bộ xử lý ngoại lệ toàn cục tại FastAPI presentation boundary."""

import logging
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# isort: split
from src.common.exceptions.base import AppException, ExceptionDetailPayload, ExceptionDetailValue
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.error_status import (
    get_error_code_for_http_status,
    get_http_status_code,
)
from src.common.logging import get_logger

logger: logging.Logger = get_logger(__name__)

PUBLIC_SERVER_MESSAGE = "Internal server error."
PUBLIC_HTTP_MESSAGE = "HTTP request failed."


def _serialize_details(
    details: tuple[ExceptionDetailPayload, ...] | None,
) -> list[dict[str, ExceptionDetailValue]] | None:
    """Chuyển exception details sang wire format chuẩn."""
    return [detail.to_dict() for detail in details] if details else None


def _public_app_message(exc: AppException, status: HTTPStatus) -> str:
    """Ẩn message kỹ thuật khỏi mọi phản hồi lỗi phía server."""
    if status.value >= HTTPStatus.INTERNAL_SERVER_ERROR.value:
        return PUBLIC_SERVER_MESSAGE
    return exc.message


def _log_app_exception(request: Request, exc: AppException, status: HTTPStatus) -> None:
    """Ghi log AppException; LLM traceback được giữ trong chain nhưng không xuất ra log."""
    log_args = (exc.code, status.value, request.url.path, exc.message)
    message = "app_exception code=%s status=%d path=%s message=%s"
    if status.value >= HTTPStatus.INTERNAL_SERVER_ERROR.value:
        if exc.code.value.startswith("LLM_"):
            logger.error(message, *log_args)
            return
        logger.error(message, *log_args, exc_info=(type(exc), exc, exc.__traceback__))
        return
    logger.info(message, *log_args)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Chuyển ``AppException`` thành error envelope chuẩn."""
    status = get_http_status_code(exc.code)
    _log_app_exception(request, exc, status)
    content: dict[str, object] = {
        "code": status.value,
        "message": _public_app_message(exc, status),
        "error_code": exc.code.value,
        "details": _serialize_details(exc.details),
    }
    return JSONResponse(status_code=status.value, content=content)


def _validation_details(exc: RequestValidationError) -> list[dict[str, str]]:
    """Chuẩn hóa từng lỗi Pydantic thành một field detail."""
    details: list[dict[str, str]] = []
    for error in exc.errors():
        location = [str(item) for item in error.get("loc", []) if item != "body"]
        details.append(
            {
                "field": ".".join(location) if location else "payload",
                "message": str(error.get("msg", "Dữ liệu không hợp lệ")),
            }
        )
    return details


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Chuyển lỗi validation thành danh sách field details."""
    details = _validation_details(exc)
    logger.warning("request_validation_failed path=%s details=%s", request.url.path, details)
    content: dict[str, object] = {
        "code": HTTPStatus.UNPROCESSABLE_ENTITY.value,
        "message": "Request validation failed.",
        "error_code": ErrorCode.VALIDATION_ERROR.value,
        "details": details,
    }
    return JSONResponse(status_code=HTTPStatus.UNPROCESSABLE_ENTITY.value, content=content)


def _http_message(status_code: int) -> str:
    """Lấy reason phrase công khai thay vì dùng exception detail tùy ý."""
    try:
        return HTTPStatus(status_code).phrase
    except ValueError:
        return PUBLIC_HTTP_MESSAGE


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Chuyển HTTP exception thành mã lỗi presentation tổng quát."""
    error_code = get_error_code_for_http_status(exc.status_code)
    logger.info("http_exception status=%d path=%s", exc.status_code, request.url.path)
    content: dict[str, object] = {
        "code": exc.status_code,
        "message": _http_message(exc.status_code),
        "error_code": error_code.value,
        "details": None,
    }
    return JSONResponse(status_code=exc.status_code, content=content)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Ẩn lỗi ngoài dự kiến và ghi đầy đủ traceback đã được redact."""
    logger.exception("unhandled_exception path=%s", request.url.path)
    content: dict[str, object] = {
        "code": HTTPStatus.INTERNAL_SERVER_ERROR.value,
        "message": PUBLIC_SERVER_MESSAGE,
        "error_code": ErrorCode.INTERNAL_SERVER_ERROR.value,
        "details": None,
    }
    return JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value, content=content)


def register_exception_handlers(app: FastAPI) -> None:
    """Đăng ký toàn bộ global exception handler cho ứng dụng.

    Args:
        app: FastAPI application cần cấu hình.
    """
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
