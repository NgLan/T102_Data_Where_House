"""DuckDB profiler nhận diện toàn bộ date/datetime format yêu cầu."""

import pytest
from src.infrastructure.storage.duckdb_csv_profiler import DuckDbCsvProfiler


@pytest.mark.parametrize("value", ["2026-08-22", "22/08/2026", "22-08-2026"])
def test_date_formats(value: str) -> None:
    column = DuckDbCsvProfiler().profile(f"event_date\n{value}\n".encode(), "events.csv").columns[0]
    assert column.date_match_ratio == 1


@pytest.mark.parametrize(
    "value",
    ["2026-08-22 12:30:45", "22/08/2026 12:30:45", "22-08-2026 12:30:45"],
)
def test_datetime_formats(value: str) -> None:
    column = DuckDbCsvProfiler().profile(f"event_at\n{value}\n".encode(), "events.csv").columns[0]
    assert column.datetime_match_ratio == 1


def test_raw_view_preserves_leading_zero() -> None:
    column = DuckDbCsvProfiler().profile(b"customer_id\n00123\n00456\n", "customers.csv").columns[0]
    assert column.has_leading_zero is True
