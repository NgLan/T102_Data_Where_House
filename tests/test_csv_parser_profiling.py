"""Kiểm thử profiling và semantic CATEGORY của CSV."""

from src.domain.data_source.enums import ColumnDataType
from src.domain.data_source.value_objects import ColumnMetadata
from src.infrastructure.storage.csv_parser import CsvParser


def _column(content: bytes, name: str) -> ColumnMetadata:
    result = CsvParser().parse(content, "profile.csv")
    return next(item for item in result.schema_metadata.tables[0].columns if item.name == name)


def test_profile_counts_nulls_distinct_and_deterministic_values() -> None:
    content = "gender,email\nNam,a@example.com\nNữ,b@example.com\nNam,\nKhác,c@example.com\n".encode()

    gender = _column(content, "gender")
    email = _column(content, "email")

    assert gender.data_type is ColumnDataType.CATEGORY
    assert gender.distinct_values == ("Nam", "Nữ", "Khác")
    assert email.nullable is True
    assert email.null_count == 1
    assert email.distinct_count == 3


def test_low_cardinality_text_is_category_on_large_dataset() -> None:
    rows = [f"{index},{'active' if index % 2 else 'inactive'}" for index in range(30)]
    status = _column(("id,status\n" + "\n".join(rows)).encode(), "status")

    assert status.data_type is ColumnDataType.CATEGORY
    assert status.distinct_values == ("inactive", "active")


def test_high_cardinality_and_identifier_text_are_not_categories() -> None:
    rows = [f"CUS-{index:03d},Customer number {index}" for index in range(30)]
    content = ("customer_id,description\n" + "\n".join(rows)).encode()

    customer_id = _column(content, "customer_id")
    description = _column(content, "description")

    assert customer_id.data_type == "TEXT"
    assert customer_id.data_type is ColumnDataType.TEXT
    assert customer_id.distinct_values == ()
    assert description.data_type is ColumnDataType.TEXT


def test_unhinted_small_unique_text_is_not_low_confidence_category() -> None:
    value = _column(b"label\nalpha\nbeta\ngamma\n", "label")

    assert value.data_type is ColumnDataType.TEXT
    assert value.distinct_values == ()
