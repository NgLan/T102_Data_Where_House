"""Bộ lọc gắn context và che dữ liệu nhạy cảm trong log."""

import logging
import re
from collections.abc import Mapping

from src.common.logging.context import (
    get_agent_name,
    get_correlation_id,
    get_request_id,
    get_session_id,
)

REDACTED_STR = "***REDACTED***"
SENSITIVE_KEY_PATTERN = (
    r"password(?:_hash)?|access_token|refresh_token|api_key|secret|"
    r"client_secret|authorization|jwt|token"
)
SENSITIVE_KEY_REGEX = re.compile(SENSITIVE_KEY_PATTERN, re.IGNORECASE)
QUOTED_VALUE_REGEX = re.compile(
    rf"(?P<prefix>[\"']?(?:{SENSITIVE_KEY_PATTERN})[\"']?\s*[:=]\s*)"
    r"(?P<quote>[\"'])(?P<value>.*?)(?P=quote)",
    re.IGNORECASE,
)
PLAIN_VALUE_REGEX = re.compile(
    rf"(?P<prefix>(?:{SENSITIVE_KEY_PATTERN})\s*=\s*)(?P<value>(?![\"'])[^\s,&]+)",
    re.IGNORECASE,
)
BEARER_TOKEN_REGEX = re.compile(r"(Bearer\s+)[a-zA-Z0-9\-._~+/]+=*", re.IGNORECASE)


def redact_sensitive_text(value: str) -> str:
    """Che secret trong chuỗi log, query string và JSON đơn giản.

    Args:
        value: Chuỗi chưa được tin cậy.

    Returns:
        Chuỗi đã thay mọi giá trị nhạy cảm nhận diện được.
    """
    redacted = BEARER_TOKEN_REGEX.sub(rf"\1{REDACTED_STR}", value)
    redacted = QUOTED_VALUE_REGEX.sub(
        lambda match: f"{match.group('prefix')}{match.group('quote')}"
        f"{REDACTED_STR}{match.group('quote')}",
        redacted,
    )
    redacted = PLAIN_VALUE_REGEX.sub(
        lambda match: f"{match.group('prefix')}{REDACTED_STR}",
        redacted,
    )
    return redacted


def redact_sensitive_value(value: object) -> object:
    """Che secret đệ quy trong dữ liệu structured log."""
    if isinstance(value, str):
        return redact_sensitive_text(value)
    if isinstance(value, Mapping):
        return {
            key: REDACTED_STR if SENSITIVE_KEY_REGEX.search(str(key)) else redact_sensitive_value(item)
            for key, item in value.items()
        }
    if isinstance(value, tuple):
        return tuple(redact_sensitive_value(item) for item in value)
    if isinstance(value, list):
        return [redact_sensitive_value(item) for item in value]
    return value


class ContextLogFilter(logging.Filter):
    """Gắn request, correlation, session và agent context vào LogRecord."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Bổ sung context còn thiếu cho một log record."""
        record.request_id = getattr(record, "request_id", None) or get_request_id() or "-"
        record.correlation_id = getattr(record, "correlation_id", None) or get_correlation_id() or "-"
        record.session_id = getattr(record, "session_id", None) or get_session_id() or "-"
        record.agent_name = getattr(record, "agent_name", None) or get_agent_name() or "-"
        return True


class SensitiveDataFilter(logging.Filter):
    """Che secret trong message, arguments và structured extras."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Thay dữ liệu nhạy cảm trước khi formatter xử lý record."""
        record.msg = redact_sensitive_value(record.msg)
        if isinstance(record.args, tuple):
            record.args = tuple(redact_sensitive_value(item) for item in record.args)
        elif isinstance(record.args, Mapping):
            record.args = {
                key: redact_sensitive_value(value) for key, value in record.args.items()
            }
        for key, value in tuple(record.__dict__.items()):
            if SENSITIVE_KEY_REGEX.search(key):
                record.__dict__[key] = REDACTED_STR
            elif key not in {"msg", "args", "exc_info"}:
                record.__dict__[key] = redact_sensitive_value(value)
        return True
