"""Kiểm thử CSV sniffer và biên lỗi của DuckDB parser."""

import duckdb
import pytest
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.infrastructure.storage.csv_parser import CsvParser


@pytest.mark.parametrize("content", [b"", b"\xef\xbb\xbf  \r\n"])
def test_empty_csv_returns_empty_schema(content: bytes) -> None:
    result = CsvParser().parse(content, "empty.csv")

    assert result.schema_metadata.tables[0].columns == ()
    assert result.preview_rows == ()
    assert result.total_rows == 0


def test_header_only_csv_preserves_columns() -> None:
    result = CsvParser().parse(b"id,name\n", "header.csv")

    assert [item.name for item in result.schema_metadata.tables[0].columns] == ["id", "name"]
    assert result.preview_rows == ()
    assert result.total_rows == 0


@pytest.mark.parametrize(
    ("content", "expected_name"),
    [
        (b"id;name\n1;Lan\n", "Lan"),
        (b'id,name\n1,"Nguyen, An"\n', "Nguyen, An"),
        (b"\xef\xbb\xbfid,name\n1,Minh\n", "Minh"),
    ],
)
def test_sniffer_handles_common_dialects(content: bytes, expected_name: str) -> None:
    result = CsvParser().parse(content, "people.csv")

    assert result.preview_rows[0]["name"] == expected_name


def test_invalid_csv_is_translated_with_exception_chain() -> None:
    with pytest.raises(InfrastructureException) as raised:
        CsvParser().parse(b"id,name\n1,\xff\n", "invalid.csv")

    assert raised.value.code == ErrorCode.FILE_PARSING_ERROR
    assert isinstance(raised.value.__cause__, duckdb.Error)
