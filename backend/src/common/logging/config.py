"""Cấu hình tập trung cho hệ thống logging."""

import io
import logging
import sys
from typing import Literal, Protocol, TextIO

from src.common.logging.filters import ContextLogFilter, SensitiveDataFilter
from src.common.logging.formatters import ConsoleFormatter, JsonFormatter

THIRD_PARTY_LOGGERS = ("sqlalchemy", "httpx", "httpcore", "urllib3")
UVICORN_LOGGERS = ("uvicorn.error", "uvicorn.access")


class LoggingSettings(Protocol):
    """Phần cấu hình tối thiểu mà logging cần sử dụng."""

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]
    log_format: Literal["console", "json"]
    app_env: Literal["development", "production", "test"]


def _utf8_stdout() -> TextIO:
    """Bảo đảm stdout thật dùng UTF-8 mà không nuốt lỗi cấu hình."""
    stream = sys.stdout
    if isinstance(stream, io.TextIOWrapper):
        stream.reconfigure(encoding="utf-8", errors="replace")
    return stream


def _select_formatter(settings: LoggingSettings) -> logging.Formatter:
    """Chọn formatter theo môi trường và cấu hình tường minh."""
    if settings.app_env == "production" or settings.log_format == "json":
        return JsonFormatter()
    return ConsoleFormatter()


def _create_handler(
    level: int,
    formatter: logging.Formatter,
) -> logging.Handler:
    """Tạo stdout handler có context và sensitive-data filter."""
    handler = logging.StreamHandler(_utf8_stdout())
    handler.setLevel(level)
    handler.setFormatter(formatter)
    handler.addFilter(ContextLogFilter())
    handler.addFilter(SensitiveDataFilter())
    return handler


def _replace_root_handlers(handler: logging.Handler, level: int) -> None:
    """Thay handler root để cấu hình lặp lại vẫn idempotent."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    for current_handler in root_logger.handlers[:]:
        root_logger.removeHandler(current_handler)
    root_logger.addHandler(handler)


def _configure_library_loggers(level: int) -> None:
    """Giảm nhiễu từ logger bên thứ ba và đồng bộ Uvicorn."""
    for logger_name in THIRD_PARTY_LOGGERS:
        library_logger = logging.getLogger(logger_name)
        library_logger.setLevel(max(level, logging.WARNING))
        library_logger.propagate = True
    for logger_name in UVICORN_LOGGERS:
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers = []
        uvicorn_logger.propagate = True


def configure_logging(settings: LoggingSettings) -> None:
    """Cấu hình logging toàn hệ thống.

    Args:
        settings: Cấu hình level, format và môi trường ứng dụng.
    """
    level = logging.getLevelNamesMapping()[settings.log_level]
    handler = _create_handler(level, _select_formatter(settings))
    _replace_root_handlers(handler, level)
    _configure_library_loggers(level)
