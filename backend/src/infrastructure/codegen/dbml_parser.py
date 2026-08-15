"""Bộ phân tích cú pháp (Parser) chuyển nội dung DBML thành cây cú pháp trung gian."""

import re

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.infrastructure.codegen.ast import (
    ParsedColumn,
    ParsedEnum,
    ParsedIndex,
    ParsedRef,
    ParsedSchema,
    ParsedTable,
)
from src.infrastructure.codegen.constants import (
    IGNORED_BLOCK_KEYWORDS,
    MAX_DBML_LENGTH,
    RELATIONSHIP_OPERATORS,
)

_BLOCK_COMMENT_PATTERN = re.compile(r"/\*.*?\*/", re.DOTALL)
_TABLE_HEADER_PATTERN = re.compile(
    r"^table\s+(?P<name>\"[^\"]+\"|[\w.]+)(?:\s+as\s+[\w\"]+)?\s*(?:\[[^\]]*\])?\s*\{$",
    re.IGNORECASE,
)
_ENUM_HEADER_PATTERN = re.compile(r"^enum\s+(?P<name>\"[^\"]+\"|[\w.]+)\s*\{$", re.IGNORECASE)
_IGNORED_HEADER_PATTERN = re.compile(r"^(?P<keyword>\w+)\b[^{]*\{$")
_INLINE_REF_PATTERN = re.compile(
    r"^ref\s*:\s*(?P<op>[<>-]{1,2})\s*(?P<target>[\w\"]+)\.(?P<column>[\w\"]+)$",
    re.IGNORECASE,
)
_STANDALONE_REF_PATTERN = re.compile(
    r"^ref\s*(?:\w+\s*)?:\s*"
    r"(?P<left_table>[\w\"]+)\.(?P<left_column>[\w\"]+)\s*"
    r"(?P<op>[<>-]{1,2})\s*"
    r"(?P<right_table>[\w\"]+)\.(?P<right_column>[\w\"]+)\s*(?:\[[^\]]*\])?$",
    re.IGNORECASE,
)
_COLUMN_PATTERN = re.compile(
    r"^(?P<name>\"[^\"]+\"|[\w]+)\s+(?P<type>\"[^\"]+\"|[\w]+(?:\s*\([^)]*\))?)"
    r"(?:\s*\[(?P<settings>.*)\])?$"
)
_INDEX_ENTRY_PATTERN = re.compile(
    r"^(?:\((?P<group>[^)]*)\)|(?P<single>[\w\"]+))\s*(?:\[(?P<settings>.*)\])?$"
)


def _fail(message: str) -> BusinessException:
    """Tạo ngoại lệ nghiệp vụ chuẩn cho lỗi cú pháp DBML."""
    return BusinessException(code=ErrorCode.INVALID_DBML_CONTENT, message=message)


def _unquote(value: str) -> str:
    """Bỏ dấu nháy bao quanh một định danh hoặc chuỗi literal."""
    stripped = value.strip()
    if len(stripped) >= 2 and stripped[0] == stripped[-1] and stripped[0] in "\"'`":
        return stripped[1:-1]
    return stripped


def _strip_line_comment(line: str) -> str:
    """Loại bỏ phần chú thích `//` nằm ngoài chuỗi literal của một dòng."""
    quote: str | None = None
    for index, char in enumerate(line):
        if quote:
            if char == quote:
                quote = None
        elif char in "\"'`":
            quote = char
        elif char == "/" and line[index + 1 : index + 2] == "/":
            return line[:index]
    return line


def _split_braces(line: str) -> list[str]:
    """Tách dấu `{`/`}` thành ranh giới dòng riêng để hỗ trợ khối viết gọn trên một dòng."""
    segments: list[str] = []
    buffer: list[str] = []
    quote: str | None = None
    for char in line:
        if quote:
            buffer.append(char)
            if char == quote:
                quote = None
            continue
        if char in "\"'`":
            quote = char
            buffer.append(char)
            continue
        if char == "{":
            buffer.append(char)
            segments.append("".join(buffer).strip())
            buffer = []
            continue
        if char == "}":
            segments.append("".join(buffer).strip())
            segments.append("}")
            buffer = []
            continue
        buffer.append(char)
    segments.append("".join(buffer).strip())
    return [segment for segment in segments if segment]


def _normalize_lines(dbml: str) -> list[str]:
    """Chuẩn hóa nội dung DBML thành danh sách dòng đã bỏ chú thích và dòng trống."""
    without_block_comments = _BLOCK_COMMENT_PATTERN.sub("\n", dbml)
    lines: list[str] = []
    for raw_line in without_block_comments.splitlines():
        cleaned = _strip_line_comment(raw_line).strip()
        if cleaned:
            lines.extend(_split_braces(cleaned))
    return lines


def _split_top_level(value: str, separator: str = ",") -> list[str]:
    """Tách chuỗi theo dấu phân cách ở mức ngoài cùng, bỏ qua phần trong ngoặc và nháy."""
    parts: list[str] = []
    buffer: list[str] = []
    depth = 0
    quote: str | None = None
    for char in value:
        if quote:
            if char == quote:
                quote = None
        elif char in "\"'`":
            quote = char
        elif char in "([":
            depth += 1
        elif char in ")]":
            depth -= 1
        elif char == separator and depth == 0:
            parts.append("".join(buffer).strip())
            buffer = []
            continue
        buffer.append(char)
    tail = "".join(buffer).strip()
    if tail:
        parts.append(tail)
    return [part for part in parts if part]


def _apply_column_setting(column: ParsedColumn, setting: str) -> str | None:
    """Áp dụng một thuộc tính cột; trả về chuỗi `ref` thô nếu thuộc tính là quan hệ."""
    lowered = setting.lower()
    if lowered in {"pk", "primary key"}:
        column.is_primary_key = True
    elif lowered in {"not null"}:
        column.is_not_null = True
    elif lowered in {"null"}:
        column.is_not_null = False
    elif lowered == "unique":
        column.is_unique = True
    elif lowered in {"increment", "autoincrement"}:
        column.is_increment = True
    elif lowered.startswith("default:"):
        column.default_value = setting.split(":", 1)[1].strip()
    elif lowered.startswith("note:"):
        column.note = _unquote(setting.split(":", 1)[1])
    elif lowered.startswith("ref:"):
        return setting
    return None


def _parse_inline_ref(raw_ref: str, table_name: str, column_name: str) -> ParsedRef | None:
    """Phân tích quan hệ khai báo trực tiếp trong thuộc tính cột (`ref: > Other.col`)."""
    match = _INLINE_REF_PATTERN.match(raw_ref.strip())
    if not match:
        return None
    operator = match.group("op")
    if operator not in RELATIONSHIP_OPERATORS:
        return None
    target_table = _unquote(match.group("target"))
    target_column = _unquote(match.group("column"))
    if operator == "<":
        return ParsedRef(target_table, target_column, table_name, column_name)
    return ParsedRef(table_name, column_name, target_table, target_column)


def _parse_column_line(line: str, table_name: str) -> tuple[ParsedColumn, ParsedRef | None]:
    """Phân tích một dòng khai báo cột trong khối `Table`."""
    match = _COLUMN_PATTERN.match(line)
    if not match:
        raise _fail(f"Không thể phân tích dòng khai báo cột trong bảng '{table_name}': {line!r}")
    column = ParsedColumn(
        name=_unquote(match.group("name")),
        raw_type=re.sub(r"\s+", "", _unquote(match.group("type"))),
    )
    ref: ParsedRef | None = None
    for setting in _split_top_level(match.group("settings") or ""):
        raw_ref = _apply_column_setting(column, setting)
        if raw_ref:
            ref = _parse_inline_ref(raw_ref, table_name, column.name)
    return column, ref


def _parse_index_entry(line: str, table_name: str) -> ParsedIndex:
    """Phân tích một dòng khai báo chỉ mục trong khối `indexes`."""
    match = _INDEX_ENTRY_PATTERN.match(line)
    if not match:
        raise _fail(f"Không thể phân tích chỉ mục của bảng '{table_name}': {line!r}")
    if match.group("group") is not None:
        columns = [_unquote(part) for part in _split_top_level(match.group("group"))]
    else:
        columns = [_unquote(match.group("single"))]
    index = ParsedIndex(columns=columns)
    for setting in _split_top_level(match.group("settings") or ""):
        lowered = setting.lower()
        if lowered in {"unique", "pk"}:
            index.is_unique = True
        elif lowered.startswith("name:"):
            index.name = _unquote(setting.split(":", 1)[1])
    return index


class _BlockReader:
    """Con trỏ duyệt danh sách dòng DBML đã chuẩn hóa."""

    def __init__(self, lines: list[str]) -> None:
        """Khởi tạo con trỏ tại dòng đầu tiên."""
        self._lines: list[str] = lines
        self.position: int = 0

    def has_next(self) -> bool:
        """Kiểm tra còn dòng chưa xử lý hay không."""
        return self.position < len(self._lines)

    def next_line(self) -> str:
        """Lấy dòng hiện tại và dịch con trỏ sang dòng kế tiếp."""
        line = self._lines[self.position]
        self.position += 1
        return line


def _read_block_body(reader: _BlockReader, block_name: str) -> list[str]:
    """Đọc toàn bộ dòng bên trong một khối `{ ... }` (hỗ trợ khối lồng nhau)."""
    body: list[str] = []
    depth = 1
    while reader.has_next():
        line = reader.next_line()
        depth += line.count("{") - line.count("}")
        if depth == 0:
            return body
        body.append(line)
    raise _fail(f"Khối '{block_name}' thiếu dấu đóng '}}'.")


def _parse_table_body(body: list[str], table: ParsedTable, schema: ParsedSchema) -> None:
    """Phân tích phần thân của khối `Table` thành cột, chỉ mục và quan hệ."""
    reader = _BlockReader(body)
    while reader.has_next():
        line = reader.next_line()
        lowered = line.lower()
        if lowered.startswith("indexes") and line.endswith("{"):
            for entry in _read_block_body(reader, f"{table.name}.indexes"):
                table.indexes.append(_parse_index_entry(entry, table.name))
            continue
        if lowered.startswith("note:"):
            table.note = _unquote(line.split(":", 1)[1])
            continue
        if lowered.startswith("note") and line.endswith("{"):
            table.note = " ".join(_read_block_body(reader, f"{table.name}.note"))
            continue
        column, ref = _parse_column_line(line, table.name)
        table.columns.append(column)
        if ref:
            schema.refs.append(ref)


def _parse_standalone_ref(line: str, schema: ParsedSchema) -> None:
    """Phân tích khai báo quan hệ độc lập dạng `Ref: A.col > B.col`."""
    match = _STANDALONE_REF_PATTERN.match(line)
    if not match:
        schema.warnings.append(f"Bỏ qua khai báo quan hệ không hỗ trợ: {line!r}")
        return
    left = (_unquote(match.group("left_table")), _unquote(match.group("left_column")))
    right = (_unquote(match.group("right_table")), _unquote(match.group("right_column")))
    operator = match.group("op")
    if operator == "<":
        schema.refs.append(ParsedRef(right[0], right[1], left[0], left[1]))
        return
    if operator == "<>":
        schema.warnings.append(
            f"Quan hệ nhiều-nhiều '{line}' không sinh được khóa ngoại, đã bỏ qua."
        )
        return
    schema.refs.append(ParsedRef(left[0], left[1], right[0], right[1]))


def _parse_enum_block(name: str, body: list[str]) -> ParsedEnum:
    """Phân tích khối `Enum` thành danh sách giá trị hợp lệ."""
    values: list[str] = []
    for line in body:
        value = _unquote(re.split(r"\s*\[", line, maxsplit=1)[0])
        if value:
            values.append(value)
    return ParsedEnum(name=name, values=values)


def _consume_block(line: str, reader: _BlockReader, schema: ParsedSchema) -> None:
    """Xử lý một khối cấp cao nhất trong nội dung DBML."""
    table_match = _TABLE_HEADER_PATTERN.match(line)
    if table_match:
        table = ParsedTable(name=_unquote(table_match.group("name")))
        _parse_table_body(_read_block_body(reader, table.name), table, schema)
        schema.tables.append(table)
        return
    enum_match = _ENUM_HEADER_PATTERN.match(line)
    if enum_match:
        name = _unquote(enum_match.group("name"))
        schema.enums.append(_parse_enum_block(name, _read_block_body(reader, name)))
        return
    ignored_match = _IGNORED_HEADER_PATTERN.match(line)
    if ignored_match and ignored_match.group("keyword").lower() in IGNORED_BLOCK_KEYWORDS:
        _read_block_body(reader, ignored_match.group("keyword"))
        return
    if line.lower().startswith("ref"):
        _parse_standalone_ref(line, schema)
        return
    schema.warnings.append(f"Bỏ qua khai báo DBML không hỗ trợ: {line!r}")


def _validate_schema(schema: ParsedSchema) -> None:
    """Kiểm tra tính toàn vẹn tối thiểu của mô hình sau khi phân tích."""
    if not schema.tables:
        raise _fail("Nội dung DBML không chứa bảng nào (không tìm thấy khối `Table`).")
    table_names = {table.name.lower() for table in schema.tables}
    valid_refs: list[ParsedRef] = []
    for ref in schema.refs:
        if ref.from_table.lower() in table_names and ref.to_table.lower() in table_names:
            valid_refs.append(ref)
        else:
            schema.warnings.append(
                f"Bỏ qua quan hệ '{ref.from_table}.{ref.from_column} > "
                f"{ref.to_table}.{ref.to_column}' vì tham chiếu tới bảng chưa được khai báo."
            )
    schema.refs = valid_refs


def parse_dbml(dbml: str) -> ParsedSchema:
    """Phân tích nội dung DBML thành cây cú pháp trung gian `ParsedSchema`."""
    if not dbml or not dbml.strip():
        raise _fail("Nội dung DBML không được để trống.")
    if len(dbml) > MAX_DBML_LENGTH:
        raise _fail(f"Nội dung DBML vượt quá giới hạn {MAX_DBML_LENGTH} ký tự.")

    schema = ParsedSchema()
    reader = _BlockReader(_normalize_lines(dbml))
    while reader.has_next():
        _consume_block(reader.next_line(), reader, schema)
    _validate_schema(schema)
    return schema
