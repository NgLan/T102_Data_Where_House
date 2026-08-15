"""Lớp cơ sở cho các bộ sinh mã DDL theo từng hệ quản trị CSDL."""

import re
from abc import ABC, abstractmethod

from src.domain.data_model.enums import SqlDialect
from src.infrastructure.codegen.ast import ParsedColumn, ParsedSchema, ParsedTable
from src.infrastructure.codegen.constants import (
    DEFAULT_VARCHAR_LENGTH,
    DIMENSION_TABLE_PREFIX,
    FACT_TABLE_PREFIX,
    FALLBACK_COLUMN_TYPE,
)

_TYPE_ARGS_PATTERN = re.compile(r"^(?P<base>[\w]+)(?:\((?P<args>[^)]*)\))?$")
_SAFE_IDENTIFIER_PATTERN = re.compile(r"^[a-z_][a-z0-9_]*$")


class BaseDialectEmitter(ABC):
    """Khung sinh mã DDL dùng chung (Template Method) cho mọi dialect."""

    dialect: SqlDialect
    quote_char: str = '"'
    supports_increment: bool = True
    supports_index: bool = True
    supports_enum_type: bool = False
    supports_unique_constraint: bool = True
    inline_foreign_key: bool = False

    def __init__(self, schema: ParsedSchema, schema_name: str) -> None:
        """Khởi tạo emitter với mô hình đã phân tích và tên schema đích."""
        self._schema: ParsedSchema = schema
        self._schema_name: str = schema_name
        self._warnings: list[str] = list(schema.warnings)

    @property
    def warnings(self) -> list[str]:
        """Danh sách cảnh báo phát sinh trong quá trình sinh mã."""
        return self._warnings

    # --- Các điểm mở rộng bắt buộc theo từng dialect ---

    @abstractmethod
    def map_type(self, column: ParsedColumn) -> str:
        """Ánh xạ kiểu dữ liệu DBML của một cột sang kiểu dữ liệu của dialect."""

    @abstractmethod
    def emit_create_schema(self) -> str:
        """Sinh câu lệnh tạo schema cách ly Sandbox."""

    @abstractmethod
    def emit_create_table_header(self, table: ParsedTable) -> str:
        """Sinh dòng mở đầu của câu lệnh tạo bảng."""

    # --- Tiện ích dùng chung ---

    def quote(self, identifier: str) -> str:
        """Bọc định danh bằng ký tự trích dẫn khi cần thiết."""
        if _SAFE_IDENTIFIER_PATTERN.match(identifier):
            return identifier
        escaped = identifier.replace(self.quote_char, self.quote_char * 2)
        return f"{self.quote_char}{escaped}{self.quote_char}"

    def qualified_name(self, table_name: str) -> str:
        """Tên bảng đầy đủ đã gắn tiền tố schema Sandbox (FR6.1)."""
        return f"{self.quote(self._schema_name)}.{self.quote(table_name)}"

    def split_type(self, raw_type: str) -> tuple[str, list[str]]:
        """Tách kiểu dữ liệu DBML thành tên cơ sở và danh sách tham số."""
        match = _TYPE_ARGS_PATTERN.match(raw_type.strip())
        if not match:
            return raw_type.strip().lower(), []
        args_group = match.group("args")
        args = [arg.strip() for arg in args_group.split(",")] if args_group else []
        return match.group("base").lower(), [arg for arg in args if arg]

    def sized_type(self, name: str, args: list[str], default_size: int | None = None) -> str:
        """Dựng kiểu dữ liệu có tham số kích thước, dùng giá trị mặc định khi thiếu."""
        if args:
            return f"{name}({', '.join(args)})"
        if default_size is not None:
            return f"{name}({default_size})"
        return name

    def is_enum_type(self, raw_type: str) -> bool:
        """Kiểm tra kiểu dữ liệu của cột có phải là Enum đã khai báo trong DBML hay không."""
        base, _ = self.split_type(raw_type)
        return base in {name.lower() for name in self._schema.enum_names}

    def fallback_type(self, raw_type: str) -> str:
        """Kiểu dữ liệu thay thế khi không tìm được ánh xạ, kèm cảnh báo."""
        self._warnings.append(
            f"Kiểu dữ liệu '{raw_type}' chưa được hỗ trợ cho {self.dialect.value}, "
            f"đã tạm ánh xạ thành {FALLBACK_COLUMN_TYPE}."
        )
        return FALLBACK_COLUMN_TYPE

    def default_varchar(self, args: list[str]) -> str:
        """Kiểu chuỗi có độ dài, dùng độ dài mặc định khi DBML không khai báo."""
        return self.sized_type("VARCHAR", args, DEFAULT_VARCHAR_LENGTH)

    # --- Sinh mã ---

    def sorted_tables(self) -> list[ParsedTable]:
        """Sắp xếp bảng theo chuẩn Kimball: Dimension trước, Fact sau, còn lại giữ nguyên."""

        def rank(item: tuple[int, ParsedTable]) -> tuple[int, int]:
            index, table = item
            lowered = table.name.lower()
            if lowered.startswith(DIMENSION_TABLE_PREFIX):
                return (0, index)
            if lowered.startswith(FACT_TABLE_PREFIX):
                return (2, index)
            return (1, index)

        return [table for _, table in sorted(enumerate(self._schema.tables), key=rank)]

    def emit_column_definition(self, column: ParsedColumn, table: ParsedTable) -> str:
        """Sinh định nghĩa của một cột bên trong câu lệnh tạo bảng."""
        parts: list[str] = [self.quote(column.name), self.map_type(column)]
        if column.is_increment:
            identity = self.emit_identity_clause()
            if identity:
                parts.append(identity)
            else:
                self._warnings.append(
                    f"{self.dialect.value} không hỗ trợ cột tự tăng, "
                    f"đã bỏ thuộc tính `increment` của '{table.name}.{column.name}'."
                )
        if column.is_not_null or (column.is_primary_key and len(table.primary_key_columns) == 1):
            parts.append("NOT NULL")
        if column.is_unique and not column.is_primary_key:
            if self.supports_unique_constraint:
                parts.append("UNIQUE")
            else:
                self._warnings.append(
                    f"{self.dialect.value} không hỗ trợ ràng buộc UNIQUE, "
                    f"đã bỏ thuộc tính `unique` của '{table.name}.{column.name}'."
                )
        if column.default_value:
            parts.append(f"DEFAULT {column.default_value}")
        return " ".join(parts)

    def emit_identity_clause(self) -> str:
        """Mệnh đề cột tự tăng của dialect (chuỗi rỗng nếu không hỗ trợ)."""
        return "GENERATED BY DEFAULT AS IDENTITY" if self.supports_increment else ""

    def emit_primary_key_constraint(self, table: ParsedTable) -> str:
        """Sinh ràng buộc khóa chính ở mức bảng."""
        columns = ", ".join(self.quote(name) for name in table.primary_key_columns)
        return f"PRIMARY KEY ({columns})"

    def emit_inline_foreign_keys(self, table: ParsedTable) -> list[str]:
        """Sinh các ràng buộc khóa ngoại đặt trực tiếp trong câu lệnh tạo bảng."""
        return []

    def emit_table_options(self, table: ParsedTable) -> str:
        """Sinh phần tùy chọn đứng sau câu lệnh tạo bảng (partition, cluster...)."""
        return ""

    def emit_create_table(self, table: ParsedTable) -> str:
        """Sinh trọn vẹn câu lệnh tạo một bảng."""
        body: list[str] = [self.emit_column_definition(col, table) for col in table.columns]
        if table.primary_key_columns:
            body.append(self.emit_primary_key_constraint(table))
        body.extend(self.emit_inline_foreign_keys(table))
        joined = ",\n    ".join(body)
        options = self.emit_table_options(table)
        comment = f"-- Bảng: {table.name}" + (f" — {table.note}" if table.note else "")
        return f"{comment}\n{self.emit_create_table_header(table)} (\n    {joined}\n){options};"

    def emit_foreign_key_statements(self) -> list[str]:
        """Sinh các câu lệnh ALTER TABLE thêm khóa ngoại (khi không đặt inline)."""
        if self.inline_foreign_key:
            return []
        statements: list[str] = []
        for ref in self._schema.refs:
            constraint = self.quote(f"fk_{ref.from_table}_{ref.from_column}".lower())
            statements.append(
                f"ALTER TABLE {self.qualified_name(ref.from_table)}\n"
                f"    ADD CONSTRAINT {constraint}\n"
                f"    FOREIGN KEY ({self.quote(ref.from_column)})\n"
                f"    REFERENCES {self.qualified_name(ref.to_table)} "
                f"({self.quote(ref.to_column)});"
            )
        return statements

    def emit_index_statements(self) -> list[str]:
        """Sinh các câu lệnh tạo chỉ mục."""
        if not self.supports_index:
            self._append_unsupported_index_warning()
            return []
        statements: list[str] = []
        for table in self._schema.tables:
            for index in table.indexes:
                columns = ", ".join(self.quote(name) for name in index.columns)
                name = index.name or f"idx_{table.name}_{'_'.join(index.columns)}".lower()
                unique = "UNIQUE " if index.is_unique else ""
                statements.append(
                    f"CREATE {unique}INDEX IF NOT EXISTS {self.quote(name)}\n"
                    f"    ON {self.qualified_name(table.name)} ({columns});"
                )
        return statements

    def _append_unsupported_index_warning(self) -> None:
        """Ghi cảnh báo khi dialect không hỗ trợ chỉ mục nhưng DBML có khai báo."""
        if any(table.indexes for table in self._schema.tables):
            self._warnings.append(
                f"{self.dialect.value} không hỗ trợ CREATE INDEX, "
                "các khai báo `indexes` trong DBML đã được bỏ qua."
            )

    def emit_enum_statements(self) -> list[str]:
        """Sinh các câu lệnh khai báo kiểu Enum (nếu dialect hỗ trợ)."""
        if not self._schema.enums:
            return []
        if not self.supports_enum_type:
            self._warnings.append(
                f"{self.dialect.value} không hỗ trợ kiểu ENUM, "
                "các cột dùng Enum đã được ánh xạ sang kiểu chuỗi."
            )
            return []
        statements: list[str] = []
        for enum in self._schema.enums:
            values = ", ".join(f"'{value}'" for value in enum.values)
            statements.append(
                f"CREATE TYPE {self.quote(self._schema_name)}.{self.quote(enum.name)} "
                f"AS ENUM ({values});"
            )
        return statements
