"""Unit tests cho common datetime utilities (test_datetime.py)."""

from datetime import UTC, datetime, timedelta, timezone

import pytest
from src.common.utils.datetime import (
    ensure_utc,
    parse_iso_datetime,
    to_isoformat,
    utc_now,
)


def test_utc_now() -> None:
    """Kiểm tra utc_now trả về datetime có timezone UTC."""
    now = utc_now()
    assert isinstance(now, datetime)
    assert now.tzinfo is not None
    assert now.tzinfo == UTC


def test_ensure_utc_with_naive_datetime() -> None:
    """Kiểm tra ensure_utc với naive datetime (chưa có tzinfo)."""
    naive_dt = datetime(2026, 8, 12, 11, 30, 0)
    utc_dt = ensure_utc(naive_dt)

    assert utc_dt.tzinfo == UTC
    assert utc_dt.year == 2026
    assert utc_dt.hour == 11


def test_ensure_utc_with_different_timezone() -> None:
    """Kiểm tra ensure_utc với timezone khác (+7)."""
    tz_plus_7 = timezone(timedelta(hours=7))
    aware_dt = datetime(2026, 8, 12, 18, 30, 0, tzinfo=tz_plus_7)

    utc_dt = ensure_utc(aware_dt)
    assert utc_dt.tzinfo == UTC
    assert utc_dt.hour == 11  # 18:30 GMT+7 = 11:30 UTC


def test_to_isoformat() -> None:
    """Kiểm tra to_isoformat tạo chuỗi chuẩn ISO 8601."""
    dt = datetime(2026, 8, 12, 11, 30, 0, tzinfo=UTC)
    iso_str = to_isoformat(dt)

    assert "2026-08-12T11:30:00+00:00" in iso_str


def test_parse_iso_datetime_valid() -> None:
    """Kiểm tra parse_iso_datetime với chuỗi ISO hợp lệ."""
    iso_str = "2026-08-12T11:30:00Z"
    dt = parse_iso_datetime(iso_str)

    assert isinstance(dt, datetime)
    assert dt.tzinfo == UTC
    assert dt.year == 2026
    assert dt.month == 8
    assert dt.day == 12


def test_parse_iso_datetime_invalid() -> None:
    """Kiểm tra parse_iso_datetime ném ValueError khi chuỗi không hợp lệ."""
    with pytest.raises(ValueError, match="Không thể parse ISO datetime"):
        parse_iso_datetime("not-a-datetime")

    with pytest.raises(ValueError, match="chuỗi không rỗng"):
        parse_iso_datetime("   ")
