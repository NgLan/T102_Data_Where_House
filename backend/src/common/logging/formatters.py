"""Formatter console và JSON cho hệ thống logging tập trung."""

import json
import logging
from datetime import UTC, datetime

from src.common.logging.filters import redact_sensitive_text, redact_sensitive_value

CONTEXT_FIELDS = ("request_id", "correlation_id", "session_id", "agent_name")
STANDARD_RECORD_FIELDS = frozenset(
    logging.LogRecord("", 0, "", 0, "", (), None).__dict__
) | {"message", "asctime", *CONTEXT_FIELDS}


def _context_values(record: logging.LogRecord) -> dict[str, object]:
    """Lấy các context field có giá trị từ log record."""
    return {
        field: value
        for field in CONTEXT_FIELDS
        if (value := getattr(record, field, None)) not in (None, "-")
    }


def _exception_text(formatter: logging.Formatter, record: logging.LogRecord) -> str | None:
    """Format và redact traceback nếu record chứa exception."""
    if not record.exc_info:
        return None
    return redact_sensitive_text(formatter.formatException(record.exc_info))


def _structured_extras(record: logging.LogRecord) -> dict[str, object]:
    """Lấy structured extras mà không lặp trường chuẩn của LogRecord."""
    return {
        key: redact_sensitive_value(value)
        for key, value in record.__dict__.items()
        if key not in STANDARD_RECORD_FIELDS and not key.startswith("_")
    }


_RESET = "\033[0m"
_GRAY = "\033[90m"
_CYAN = "\033[36m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_BOLD_RED = "\033[1;31m"
_BLUE = "\033[34m"

_LEVEL_COLORS: dict[str, str] = {
    "DEBUG": _CYAN,
    "INFO": _GREEN,
    "WARNING": _YELLOW,
    "ERROR": _RED,
    "CRITICAL": _BOLD_RED,
}


class ConsoleFormatter(logging.Formatter):
    """Định dạng log màu sắc trực quan cho terminal phát triển."""

    def format(self, record: logging.LogRecord) -> str:
        """Chuyển record thành một dòng console có màu sắc, context và traceback."""
        timestamp = datetime.fromtimestamp(record.created, tz=UTC).strftime("%Y-%m-%d %H:%M:%S")
        level_color = _LEVEL_COLORS.get(record.levelname, "")
        context = "".join(f" [{key}={value}]" for key, value in _context_values(record).items())
        message = redact_sensitive_text(record.getMessage())
        output = (
            f"{_GRAY}{timestamp}{_RESET} | "
            f"{level_color}{record.levelname:<8}{_RESET} | "
            f"{_BLUE}{record.name}{_RESET} | "
            f"{message}"
            f"{_GRAY}{context}{_RESET}"
        )
        exception = _exception_text(self, record)
        return f"{output}\n{exception}" if exception else output



class JsonFormatter(logging.Formatter):
    """Xuất structured log JSON cho môi trường production."""

    def format(self, record: logging.LogRecord) -> str:
        """Chuyển record thành JSON gồm context, extras và traceback an toàn."""
        log_data: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": redact_sensitive_text(record.getMessage()),
            **_context_values(record),
            **_structured_extras(record),
        }
        if exception := _exception_text(self, record):
            log_data["exception"] = exception
        return json.dumps(log_data, ensure_ascii=False, default=str)
