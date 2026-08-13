"""Unit tests cho common collections utilities (test_collections.py)."""

import pytest
from src.common.utils.collections import chunked, is_empty


def test_chunked() -> None:
    """Kiểm tra chunked chia danh sách thành các chunk nhỏ."""
    data = [1, 2, 3, 4, 5, 6, 7]
    chunks = chunked(data, size=3)

    assert len(chunks) == 3
    assert chunks[0] == [1, 2, 3]
    assert chunks[1] == [4, 5, 6]
    assert chunks[2] == [7]


def test_chunked_empty_list() -> None:
    """Kiểm tra chunked với danh sách rỗng."""
    chunks = chunked([], size=5)
    assert chunks == []


def test_chunked_invalid_size() -> None:
    """Kiểm tra chunked ném ValueError nếu size < 1."""
    with pytest.raises(ValueError, match="phải lớn hơn hoặc bằng 1"):
        chunked([1, 2, 3], size=0)


def test_is_empty() -> None:
    """Kiểm tra is_empty với các tập hợp khác nhau."""
    assert is_empty(None) is True
    assert is_empty([]) is True
    assert is_empty({}) is True
    assert is_empty(set()) is True
    assert is_empty(()) is True
    assert is_empty([1, 2]) is False
    assert is_empty({"a": 1}) is False
