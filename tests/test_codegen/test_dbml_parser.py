"""Kiểm thử bộ phân tích cú pháp DBML."""

import pytest
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.infrastructure.codegen.dbml_parser import parse_dbml


def test_parse_ride_hailing_tables(ride_hailing_dbml: str) -> None:
    """Phân tích đúng số bảng, tên bảng và số cột của mô hình mẫu."""
    schema = parse_dbml(ride_hailing_dbml)

    assert [table.name for table in schema.tables] == [
        "Fact_Rides",
        "Dim_Driver",
        "Dim_Customer",
    ]
    assert len(schema.tables[0].columns) == 7
    assert len(schema.tables[1].columns) == 5
    assert len(schema.tables[2].columns) == 3


def test_parse_column_settings(ride_hailing_dbml: str) -> None:
    """Đọc đúng các thuộc tính `pk` và `increment` của cột."""
    schema = parse_dbml(ride_hailing_dbml)
    ride_key = schema.tables[0].columns[0]

    assert ride_key.name == "ride_key"
    assert ride_key.raw_type == "int"
    assert ride_key.is_primary_key is True
    assert ride_key.is_increment is True
    assert schema.tables[0].primary_key_columns == ["ride_key"]


def test_parse_inline_references(ride_hailing_dbml: str) -> None:
    """Trích xuất đúng quan hệ khóa ngoại khai báo inline trong cột."""
    schema = parse_dbml(ride_hailing_dbml)
    pairs = {(ref.from_column, ref.to_table, ref.to_column) for ref in schema.refs}

    assert pairs == {
        ("driver_key", "Dim_Driver", "driver_key"),
        ("customer_key", "Dim_Customer", "customer_key"),
    }
    assert all(ref.from_table == "Fact_Rides" for ref in schema.refs)


def test_parse_standalone_ref_and_reverse_direction() -> None:
    """Khai báo `Ref` độc lập được đọc đúng, kể cả khi đảo chiều bằng toán tử `<`."""
    dbml = """
    Table a {
      id int [pk]
    }
    Table b {
      id int [pk]
      a_id int
    }
    Ref: b.a_id > a.id
    Ref: a.id < b.a_id
    """
    schema = parse_dbml(dbml)

    assert len(schema.refs) == 2
    for ref in schema.refs:
        assert (ref.from_table, ref.from_column) == ("b", "a_id")
        assert (ref.to_table, ref.to_column) == ("a", "id")


def test_parse_indexes_block() -> None:
    """Đọc đúng khối `indexes` gồm chỉ mục đơn và chỉ mục ghép."""
    dbml = """
    Table t {
      a int [pk]
      b int
      indexes {
        (a, b) [name: 'idx_ab']
        b [unique]
      }
    }
    """
    schema = parse_dbml(dbml)
    indexes = schema.tables[0].indexes

    assert len(indexes) == 2
    assert indexes[0].columns == ["a", "b"]
    assert indexes[0].name == "idx_ab"
    assert indexes[0].is_unique is False
    assert indexes[1].columns == ["b"]
    assert indexes[1].is_unique is True


def test_parse_ignores_comments_and_unsupported_blocks() -> None:
    """Bỏ qua chú thích và các khối `Project`/`Note` mà không làm hỏng kết quả."""
    dbml = """
    Project demo { database_type: 'PostgreSQL' }
    // chú thích một dòng
    /* chú thích
       nhiều dòng */
    Table t {
      a int [pk] // chú thích cuối dòng
      note: 'Bảng thử nghiệm'
    }
    """
    schema = parse_dbml(dbml)

    assert len(schema.tables) == 1
    assert schema.tables[0].columns[0].name == "a"
    assert schema.tables[0].note == "Bảng thử nghiệm"


def test_parse_enum_block() -> None:
    """Đọc đúng khối `Enum` và danh sách giá trị."""
    dbml = """
    Enum trip_status {
      completed
      cancelled
    }
    Table t {
      a trip_status [pk]
    }
    """
    schema = parse_dbml(dbml)

    assert schema.enum_names == {"trip_status"}
    assert schema.enums[0].values == ["completed", "cancelled"]


def test_parse_drops_reference_to_unknown_table() -> None:
    """Quan hệ trỏ tới bảng chưa khai báo bị loại bỏ và ghi vào cảnh báo."""
    dbml = """
    Table t {
      a int [pk, ref: > khong_ton_tai.id]
    }
    """
    schema = parse_dbml(dbml)

    assert schema.refs == []
    assert any("khong_ton_tai" in warning for warning in schema.warnings)


@pytest.mark.parametrize(
    "invalid_dbml",
    ["", "   ", "// chỉ có chú thích", "Table t { a }"],
    ids=["empty", "whitespace", "comment_only", "malformed_column"],
)
def test_parse_invalid_dbml_raises_business_exception(invalid_dbml: str) -> None:
    """DBML rỗng hoặc sai cú pháp phải ném BusinessException với mã INVALID_DBML_CONTENT."""
    with pytest.raises(BusinessException) as exc_info:
        parse_dbml(invalid_dbml)

    assert exc_info.value.code == ErrorCode.INVALID_DBML_CONTENT


def test_parse_unclosed_block_raises_business_exception() -> None:
    """Khối `Table` thiếu dấu đóng phải bị từ chối rõ ràng."""
    with pytest.raises(BusinessException) as exc_info:
        parse_dbml("Table t {\n  a int [pk]\n")

    assert exc_info.value.code == ErrorCode.INVALID_DBML_CONTENT
