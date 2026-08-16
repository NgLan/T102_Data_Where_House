"""Kiểm thử PII Guard — che thông tin cá nhân trước khi gửi sang LLM (FR6.2)."""

import pytest
from src.infrastructure.security.pii_guard import PLACEHOLDER_PREFIX, PiiGuard

RIDE_HAILING_DBML = """// Định nghĩa Fact & Dimension Tables
Table Fact_Rides {
  ride_key int [pk, increment]
  driver_key int [ref: > Dim_Driver.driver_key]
  customer_key int [ref: > Dim_Customer.customer_key]
  fare_amount decimal(10,2)
  trip_status varchar(20)
  created_at timestamp
}

Table Dim_Driver {
  driver_key int [pk]
  driver_natural_id varchar(50)
  full_name varchar(100)
  phone_number varchar(20)
}

Table Dim_Customer {
  customer_key int [pk]
  phone_number varchar(20)
  email varchar(120)
  member_tier varchar(20)
}"""


@pytest.fixture
def guard() -> PiiGuard:
    """Bộ che PII ở trạng thái bật."""
    return PiiGuard(enabled=True)


# --- Che tên cột trong DBML ---------------------------------------------------


def test_mask_schema_replaces_sensitive_column_names(guard: PiiGuard) -> None:
    """Tên cột nhạy cảm bị thay bằng mã ẩn danh, không còn xuất hiện trong nội dung gửi đi."""
    payload = guard.mask_schema(RIDE_HAILING_DBML)

    assert "phone_number" not in payload.text
    assert "email" not in payload.text
    assert "full_name" not in payload.text
    assert PLACEHOLDER_PREFIX in payload.text


def test_mask_schema_keeps_non_sensitive_columns_untouched(guard: PiiGuard) -> None:
    """Cột nghiệp vụ bình thường phải giữ nguyên để AI không mất ngữ cảnh thiết kế."""
    payload = guard.mask_schema(RIDE_HAILING_DBML)

    for column in ("driver_key", "customer_key", "fare_amount", "trip_status", "member_tier"):
        assert column in payload.text


def test_mask_schema_keeps_table_names_untouched(guard: PiiGuard) -> None:
    """Tên bảng không phải PII nên không được đụng tới."""
    payload = guard.mask_schema(RIDE_HAILING_DBML)

    for table in ("Fact_Rides", "Dim_Driver", "Dim_Customer"):
        assert table in payload.text


def test_mask_schema_reuses_one_placeholder_per_column_name(guard: PiiGuard) -> None:
    """`phone_number` xuất hiện ở hai bảng nhưng chỉ dùng chung một mã thay thế."""
    payload = guard.mask_schema(RIDE_HAILING_DBML)

    # 3 cột nhạy cảm khác nhau: full_name, phone_number, email
    assert payload.masked_count == 3


def test_unmask_restores_original_dbml(guard: PiiGuard) -> None:
    """Che rồi hoàn nguyên phải trả về đúng nội dung ban đầu (vòng tròn khép kín)."""
    payload = guard.mask_schema(RIDE_HAILING_DBML)

    restored = guard.unmask(payload.text, payload.mapping)

    assert restored == RIDE_HAILING_DBML


def test_mask_schema_is_noop_when_no_sensitive_column(guard: PiiGuard) -> None:
    """DBML không có cột nhạy cảm thì giữ nguyên và không sinh ánh xạ."""
    dbml = "Table Dim_Vehicle {\n  vehicle_key int [pk]\n  vehicle_type varchar(30)\n}"

    payload = guard.mask_schema(dbml)

    assert payload.text == dbml
    assert payload.mapping == {}


# --- Che giá trị PII trong văn bản tự do --------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected_placeholder"),
    [
        ("liên hệ qua a.nguyen@example.com nhé", "[PII_EMAIL]"),
        ("số điện thoại 0901234567", "[PII_PHONE]"),
        ("số điện thoại +84901234567", "[PII_PHONE]"),
        ("căn cước 012345678901", "[PII_NATIONAL_ID]"),
    ],
    ids=["email", "phone_local", "phone_intl", "national_id"],
)
def test_mask_free_text_hides_pii_values(
    guard: PiiGuard, raw: str, expected_placeholder: str
) -> None:
    """Giá trị PII trong câu lệnh người dùng bị che trước khi gửi lên LLM."""
    masked = guard.mask_free_text(raw)

    assert expected_placeholder in masked


def test_mask_free_text_removes_the_original_value(guard: PiiGuard) -> None:
    """Giá trị gốc không được còn sót lại trong chuỗi đã che."""
    masked = guard.mask_free_text("thêm cột liên hệ, ví dụ 0901234567 và a@b.com")

    assert "0901234567" not in masked
    assert "a@b.com" not in masked


def test_mask_free_text_keeps_the_actual_instruction(guard: PiiGuard) -> None:
    """Phần nội dung nghiệp vụ của câu lệnh phải giữ nguyên để AI vẫn hiểu yêu cầu."""
    masked = guard.mask_free_text("Tách bảng Dim_Driver thành Dim_Driver và Dim_Vehicle")

    assert masked == "Tách bảng Dim_Driver thành Dim_Driver và Dim_Vehicle"


# --- Phát hiện mã còn sót (chốt chặn fail-closed) -----------------------------


def test_has_residual_placeholder_detects_leftover_code(guard: PiiGuard) -> None:
    """Phát hiện được mã thay thế còn sót khi LLM tự đổi định dạng."""
    assert guard.has_residual_placeholder("Table t {\n  pii_field_1 varchar(20)\n}") is True


def test_has_residual_placeholder_returns_false_for_clean_text(guard: PiiGuard) -> None:
    """DBML đã hoàn nguyên trọn vẹn thì không còn mã thay thế nào."""
    assert guard.has_residual_placeholder(RIDE_HAILING_DBML) is False


def test_unmask_leaves_residual_when_llm_renames_placeholder(guard: PiiGuard) -> None:
    """LLM đổi `pii_field_01` thành `pii_field_1` thì hoàn nguyên hụt và bị phát hiện."""
    payload = guard.mask_schema(RIDE_HAILING_DBML)
    corrupted = payload.text.replace("pii_field_01", "pii_field_1")

    restored = guard.unmask(corrupted, payload.mapping)

    assert guard.has_residual_placeholder(restored) is True


# --- Trạng thái tắt -----------------------------------------------------------


def test_disabled_guard_is_a_noop() -> None:
    """Khi tắt cấu hình, mọi dữ liệu đi thẳng không qua xử lý."""
    disabled = PiiGuard(enabled=False)

    payload = disabled.mask_schema(RIDE_HAILING_DBML)

    assert payload.text == RIDE_HAILING_DBML
    assert payload.mapping == {}
    assert disabled.mask_free_text("gọi 0901234567") == "gọi 0901234567"
