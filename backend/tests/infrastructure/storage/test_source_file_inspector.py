"""Contract tests cho parser source chạy hoàn toàn ở backend."""

from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

import pytest
from src.common.exceptions.infrastructure import InfrastructureException
from src.infrastructure.storage.source_file_inspector import SourceFileInspector


def test_tsv_preserves_quoted_tab_and_profiles() -> None:
    inspector = SourceFileInspector()
    content = b'id\tnote\n1\t"hello\tworld"\n'

    inspector.validate(content, "orders.tsv")
    preview = inspector.preview(content, "orders.tsv", None)

    assert preview.table_name == "orders"
    assert preview.rows == ({"id": "1", "note": "hello\tworld"},)
    assert inspector.profile(content, "orders.tsv").tables[0].columns[0].physical_type == "BIGINT"


def test_markdown_uses_heading_and_supports_table_selection() -> None:
    content = b"# Orders\n\nid | total\n---|---\n1|10\n\n# Users\n\nid|name\n---|---\n2|Lan\n"
    preview = SourceFileInspector().preview(content, "source.md", "Users")

    assert preview.available_tables == ("Orders", "Users")
    assert preview.rows == ({"id": "2", "name": "Lan"},)


def test_sql_reads_ddl_and_literal_insert_without_execution() -> None:
    content = b"""
        CREATE TABLE orders (id INT PRIMARY KEY, code TEXT UNIQUE);
        INSERT INTO orders VALUES (1, 'A');
        DROP TABLE users;
    """
    inspector = SourceFileInspector()

    preview = inspector.preview(content, "schema.sql", None)
    metadata = inspector.profile(content, "schema.sql").tables[0].declared_columns

    assert preview.rows == ({"id": "1", "code": "A"},)
    assert metadata is not None and metadata[0].primary_key is True
    assert metadata[1].constraints[0].type.value == "UNIQUE"


def test_xlsx_parses_multiple_sheets() -> None:
    content = _xlsx_bytes()
    inspector = SourceFileInspector()

    inspector.validate(content, "book.xlsx")
    preview = inspector.preview(content, "book.xlsx", "Users")

    assert preview.available_tables == ("Orders", "Users")
    assert preview.rows == ({"id": "2", "name": "Lan"},)


def test_duplicate_headers_are_rejected() -> None:
    with pytest.raises(InfrastructureException):
        SourceFileInspector().validate(b"id,id\n1,2\n", "bad.csv")


def _xlsx_bytes() -> bytes:
    stream = BytesIO()
    with ZipFile(stream, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", _content_types())
        archive.writestr("_rels/.rels", _root_relationships())
        archive.writestr("xl/workbook.xml", _workbook())
        archive.writestr("xl/_rels/workbook.xml.rels", _workbook_relationships())
        archive.writestr("xl/worksheets/sheet1.xml", _sheet(("id", "total"), (1, 10)))
        archive.writestr("xl/worksheets/sheet2.xml", _sheet(("id", "name"), (2, "Lan")))
    return stream.getvalue()


def _content_types() -> str:
    return """<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>"""


def _root_relationships() -> str:
    return """<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>"""


def _workbook() -> str:
    return """<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Orders" sheetId="1" r:id="rId1"/><sheet name="Users" sheetId="2" r:id="rId2"/></sheets></workbook>"""


def _workbook_relationships() -> str:
    return """<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/></Relationships>"""


def _sheet(headers: tuple[str, str], values: tuple[int, int | str]) -> str:
    second = f'<c r="B2" t="inlineStr"><is><t>{values[1]}</t></is></c>' if isinstance(values[1], str) else f'<c r="B2"><v>{values[1]}</v></c>'
    return f'''<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>{headers[0]}</t></is></c><c r="B1" t="inlineStr"><is><t>{headers[1]}</t></is></c></row><row r="2"><c r="A2"><v>{values[0]}</v></c>{second}</row></sheetData></worksheet>'''
