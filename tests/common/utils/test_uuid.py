"""Unit tests cho common UUID utilities (test_uuid.py)."""

import uuid

from src.common.utils.uuid import (
    generate_uuid,
    generate_uuid_str,
    is_valid_uuid,
)


def test_generate_uuid() -> None:
    """Kiểm tra generate_uuid sinh UUID4 hợp lệ và duy nhất."""
    id1 = generate_uuid()
    id2 = generate_uuid()

    assert isinstance(id1, uuid.UUID)
    assert isinstance(id2, uuid.UUID)
    assert id1 != id2
    assert id1.version == 4


def test_generate_uuid_str() -> None:
    """Kiểm tra generate_uuid_str sinh chuỗi UUID4 36 ký tự."""
    uuid_str1 = generate_uuid_str()
    uuid_str2 = generate_uuid_str()

    assert isinstance(uuid_str1, str)
    assert len(uuid_str1) == 36
    assert uuid_str1 != uuid_str2
    assert is_valid_uuid(uuid_str1)


def test_is_valid_uuid() -> None:
    """Kiểm tra is_valid_uuid với các loại input khác nhau."""
    valid_str = "550e8400-e29b-41d4-a716-446655440000"
    valid_obj = uuid.UUID(valid_str)
    version_one = "123e4567-e89b-12d3-a456-426614174000"

    assert is_valid_uuid(valid_obj) is True
    assert is_valid_uuid(valid_str) is True
    assert is_valid_uuid(valid_str.upper()) is True
    assert is_valid_uuid(version_one) is False
    assert is_valid_uuid("invalid-uuid-string") is False
    assert is_valid_uuid(12345) is False  # type: ignore[arg-type]
    assert is_valid_uuid(None) is False  # type: ignore[arg-type]
