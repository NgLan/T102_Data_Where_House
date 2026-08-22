"""Kiểm thử ánh xạ kiểu vật lý CSV từ DuckDB sang Domain metadata."""

from src.infrastructure.storage.csv_parser import CsvParser


def test_parser_maps_supported_physical_types() -> None:
    content = (
        "id,amount,ratio,active,birth_date,created_at,name\n"
        "1,10.250,1e100,true,2026-08-20,2026-08-20 09:30:00,An\n"
        "2,20.500,2e100,false,2026-08-21,2026-08-21 10:45:00,Bình\n"
    ).encode()

    result = CsvParser().parse(content, "customers.csv")
    columns = {column.name: column for column in result.schema_metadata.tables[0].columns}

    assert columns["id"].data_type == "INTEGER"
    assert columns["amount"].data_type == "DECIMAL"
    assert columns["ratio"].data_type == "NUMBER"
    assert columns["active"].data_type == "BOOLEAN"
    assert columns["birth_date"].data_type == "DATE"
    assert columns["created_at"].data_type == "DATETIME"
    assert columns["name"].data_type == "TEXT"
    assert result.preview_rows[0]["amount"] == "10.250"
    assert result.total_rows == 2


def test_scientific_decimal_is_not_truncated_to_integer() -> None:
    result = CsvParser().parse(b"value\n1e-3\n2e-3\n", "metrics.csv")

    column = result.schema_metadata.tables[0].columns[0]
    assert column.data_type == "DECIMAL"
    assert result.preview_rows == ({"value": "0.001"}, {"value": "0.002"})
