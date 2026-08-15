"""Bộ sinh mã DDL cho PostgreSQL."""

from src.domain.data_model.enums import SqlDialect
from src.infrastructure.codegen.ast import ParsedColumn, ParsedTable
from src.infrastructure.codegen.dialects.base import BaseDialectEmitter


class PostgresqlEmitter(BaseDialectEmitter):
    """Sinh script DDL tương thích PostgreSQL 16."""

    dialect: SqlDialect = SqlDialect.POSTGRESQL
    quote_char: str = '"'
    supports_increment: bool = True
    supports_index: bool = True
    supports_enum_type: bool = True
    inline_foreign_key: bool = False

    _SIMPLE_TYPES: dict[str, str] = {
        "int": "INTEGER",
        "integer": "INTEGER",
        "int4": "INTEGER",
        "smallint": "SMALLINT",
        "bigint": "BIGINT",
        "int8": "BIGINT",
        "serial": "INTEGER",
        "bigserial": "BIGINT",
        "text": "TEXT",
        "boolean": "BOOLEAN",
        "bool": "BOOLEAN",
        "float": "DOUBLE PRECISION",
        "double": "DOUBLE PRECISION",
        "real": "REAL",
        "date": "DATE",
        "time": "TIME",
        "timestamp": "TIMESTAMP",
        "datetime": "TIMESTAMP",
        "timestamptz": "TIMESTAMP WITH TIME ZONE",
        "uuid": "UUID",
        "json": "JSONB",
        "jsonb": "JSONB",
        "bytea": "BYTEA",
    }

    def map_type(self, column: ParsedColumn) -> str:
        """Ánh xạ kiểu DBML sang kiểu dữ liệu PostgreSQL."""
        base, args = self.split_type(column.raw_type)
        if self.is_enum_type(column.raw_type):
            return f"{self.quote(self._schema_name)}.{self.quote(base)}"
        if base in self._SIMPLE_TYPES:
            return self._SIMPLE_TYPES[base]
        if base in {"varchar", "character varying", "string"}:
            return self.default_varchar(args)
        if base == "char":
            return self.sized_type("CHAR", args, 1)
        if base in {"decimal", "numeric"}:
            return self.sized_type("NUMERIC", args)
        return self.fallback_type(column.raw_type)

    def emit_create_schema(self) -> str:
        """Sinh câu lệnh tạo schema cách ly Sandbox."""
        return f"CREATE SCHEMA IF NOT EXISTS {self.quote(self._schema_name)};"

    def emit_create_table_header(self, table: ParsedTable) -> str:
        """Sinh dòng mở đầu câu lệnh tạo bảng của PostgreSQL."""
        return f"CREATE TABLE IF NOT EXISTS {self.qualified_name(table.name)}"
