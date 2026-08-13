"""Unit tests cho common string utilities (test_string.py)."""

import pytest
from src.common.utils.string import (
    is_blank,
    normalize_whitespace,
    safe_strip,
    truncate,
)


def test_normalize_whitespace() -> None:
    """Kiểm tra normalize_whitespace chuẩn hóa khoảng trắng thừa."""
    text = "  Hello   World \t \n  Python  "
    normalized = normalize_whitespace(text)
    assert normalized == "Hello World Python"

    # Kiểm tra bảo toàn tiếng Việt và Nhật
    vietnamese = "  Xin   chào   Việt   Nam  "
    assert normalize_whitespace(vietnamese) == "Xin chào Việt Nam"


def test_normalize_whitespace_invalid_type() -> None:
    """Kiểm tra normalize_whitespace ném TypeError nếu input không phải str."""
    with pytest.raises(TypeError):
        normalize_whitespace(123)  # type: ignore[arg-type]


def test_is_blank() -> None:
    """Kiểm tra is_blank nhận diện chuỗi rỗng và None."""
    assert is_blank(None) is True
    assert is_blank("") is True
    assert is_blank("   \t\n  ") is True
    assert is_blank("a") is False
    assert is_blank(" Hello ") is False


def test_truncate() -> None:
    """Kiểm tra truncate cắt ngắn chuỗi an toàn."""
    text = "Hệ thống AI phân tích yêu cầu phần mềm"
    truncated = truncate(text, max_length=20, suffix="...")

    assert len(truncated) == 20
    assert truncated == "Hệ thống AI phân ..."

    # Không cắt nếu ngắn hơn max_length
    short_text = "Short"
    assert truncate(short_text, max_length=10) == "Short"


def test_truncate_invalid_max_length() -> None:
    """Kiểm tra truncate ném ValueError nếu max_length <= len(suffix)."""
    with pytest.raises(ValueError, match="phải lớn hơn độ dài suffix"):
        truncate("Hello World", max_length=3, suffix="...")


def test_safe_strip() -> None:
    """Kiểm tra safe_strip strip khoảng trắng an toàn."""
    assert safe_strip("  abc  ") == "abc"
    assert safe_strip(None) is None
    assert safe_strip("") == ""
