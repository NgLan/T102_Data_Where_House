"""Unit tests cho common JSON utilities (test_json.py)."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum

import pytest
from pydantic import BaseModel
from src.common.utils.json import safe_json_dumps, safe_json_loads


class StatusEnum(StrEnum):
    """Enum ví dụ cho unit test."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class SampleModel(BaseModel):
    """Pydantic model ví dụ cho unit test."""

    name: str
    age: int


def test_safe_json_dumps_custom_types() -> None:
    """Kiểm tra safe_json_dumps serialize UUID, datetime, Enum, Decimal, Pydantic model."""
    uid = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
    dt = datetime(2026, 8, 12, 11, 30, 0, tzinfo=UTC)
    enum_val = StatusEnum.ACTIVE
    decimal_val = Decimal("10.5")
    model_val = SampleModel(name="Alice", age=30)

    data = {
        "id": uid,
        "created_at": dt,
        "status": enum_val,
        "amount": decimal_val,
        "user": model_val,
    }

    json_str = safe_json_dumps(data)
    assert isinstance(json_str, str)

    parsed = safe_json_loads(json_str)
    assert parsed["id"] == "123e4567-e89b-12d3-a456-426614174000"
    assert parsed["created_at"] == "2026-08-12T11:30:00+00:00"
    assert parsed["status"] == "active"
    assert parsed["amount"] == 10.5
    assert parsed["user"] == {"name": "Alice", "age": 30}


def test_safe_json_dumps_unserializable_type() -> None:
    """Kiểm tra safe_json_dumps ném TypeError với type không hỗ trợ."""

    class UnserializableObject:
        pass

    with pytest.raises(TypeError):
        safe_json_dumps({"obj": UnserializableObject()})


def test_safe_json_loads_valid() -> None:
    """Kiểm tra safe_json_loads parse chuỗi JSON hợp lệ."""
    json_str = '{"key": "value", "count": 5}'
    parsed = safe_json_loads(json_str)

    assert parsed == {"key": "value", "count": 5}


def test_safe_json_loads_invalid() -> None:
    """Kiểm tra safe_json_loads ném ValueError khi JSON không hợp lệ."""
    with pytest.raises(ValueError, match="Chuỗi JSON không đúng định dạng"):
        safe_json_loads("{invalid json}")

    with pytest.raises(ValueError, match="Chuỗi JSON đầu vào không được rỗng"):
        safe_json_loads("   ")
