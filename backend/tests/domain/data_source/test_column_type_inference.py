"""Unit tests cho rule inference thuần Domain."""

import pytest
from src.domain.data_source.column_profile import ColumnProfile
from src.domain.data_source.column_type_inference import infer_logical_type
from src.domain.data_source.enums import ColumnDataType


def profile(name: str, **changes: object) -> ColumnProfile:
    """Tạo profile mặc định đủ tín hiệu cho test."""
    values = {
        "physical_type": "VARCHAR",
        "total_rows": 100,
        "distinct_count": 5,
        "average_length": 8.0,
        "top_value_ratio": 0.4,
    }
    values.update(changes)
    return ColumnProfile(name=name, **values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "item",
    [
        profile("customer_id", physical_type="BIGINT", distinct_count=100),
        profile("account_number", physical_type="BIGINT", distinct_count=100, has_leading_zero=True),
    ],
)
def test_identifier_is_text(item: ColumnProfile) -> None:
    assert infer_logical_type(item).data_type is ColumnDataType.TEXT


def test_identifier_hint_does_not_match_inside_another_word() -> None:
    decision = infer_logical_type(profile("paid_amount", physical_type="DECIMAL(10,2)"))
    assert decision.data_type is ColumnDataType.DECIMAL


@pytest.mark.parametrize("name", ["note", "description", "ghi_chu"])
def test_free_text_is_not_category(name: str) -> None:
    assert infer_logical_type(profile(name)).data_type is ColumnDataType.TEXT


@pytest.mark.parametrize("name", ["status", "gender", "gioi_tinh"])
def test_semantic_low_cardinality_is_category(name: str) -> None:
    assert infer_logical_type(profile(name)).data_type is ColumnDataType.CATEGORY


def test_cardinality_without_semantic_hint_is_not_category() -> None:
    assert infer_logical_type(profile("value")).data_type is ColumnDataType.TEXT


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("date_match_ratio", ColumnDataType.DATE),
        ("datetime_match_ratio", ColumnDataType.DATETIME),
    ],
)
def test_date_threshold(field: str, expected: ColumnDataType) -> None:
    assert infer_logical_type(profile("event_at", **{field: 0.95})).data_type is expected
