"""Kiểu cấu hình LLM parse được CSV/JSON mà không làm lộ secret."""

import json
from typing import Annotated

from pydantic import BeforeValidator, SecretStr
from pydantic_settings import NoDecode


def _parse_items(value: object) -> tuple[str, ...]:
    """Chuẩn hóa một list cấu hình từ CSV, JSON hoặc sequence."""
    if value is None:
        return ()
    if isinstance(value, str):
        items = _parse_string(value)
    elif isinstance(value, (list, tuple)):
        items = tuple(str(item).strip() for item in value)
    else:
        raise ValueError("Danh sách cấu hình LLM không đúng định dạng.")
    if any(not item for item in items):
        raise ValueError("Danh sách cấu hình LLM không được chứa phần tử rỗng.")
    if len(set(items)) != len(items):
        raise ValueError("Danh sách cấu hình LLM không được chứa phần tử trùng.")
    return items


def _parse_string(value: str) -> tuple[str, ...]:
    normalized = value.strip()
    if not normalized:
        return ()
    if normalized.startswith("["):
        decoded = json.loads(normalized)
        if not isinstance(decoded, list):
            raise ValueError("Danh sách cấu hình LLM JSON phải là array.")
        return tuple(str(item).strip() for item in decoded)
    return tuple(item.strip() for item in normalized.split(","))


def _parse_secrets(value: object) -> tuple[SecretStr, ...]:
    """Bọc từng credential đã chuẩn hóa bằng SecretStr."""
    if isinstance(value, tuple) and all(isinstance(item, SecretStr) for item in value):
        raw = tuple(item.get_secret_value() for item in value)
    else:
        raw = _parse_items(value)
    return tuple(SecretStr(item.strip()) for item in raw)


StringListSetting = Annotated[tuple[str, ...], NoDecode, BeforeValidator(_parse_items)]
SecretListSetting = Annotated[tuple[SecretStr, ...], NoDecode, BeforeValidator(_parse_secrets)]

