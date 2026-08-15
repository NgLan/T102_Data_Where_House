"""Bộ sinh mã DDL cho Snowflake."""

from src.domain.data_model.enums import SqlDialect
from src.infrastructure.codegen.ast import ParsedColumn, ParsedTable
from src.infrastructure.codegen.dialects.base import BaseDialectEmitter


class SnowflakeEmitter(BaseDialectEmitter):
    """Sinh script DDL tương thích Snowflake.

    Snowflake chấp nhận khai báo PRIMARY KEY / FOREIGN KEY nhưng không thực thi ràng buộc
    (không enforce), và không hỗ trợ CREATE INDEX.
    """

    dialect: SqlDialect = SqlDialect.SNOWFLAKE
    quote_char: str = '"'
    supports_increment: bool = True
    supports_index: bool = False
    supports_enum_type: bool = False
    inline_foreign_key: bool = False

    _SIMPLE_TYPES: dict[str, str] = {
        "int": "NUMBER(38,0)",
        "integer": "NUMBER(38,0)",
        "int4": "NUMBER(38,0)",
        "int8": "NUMBER(38,0)",
        "smallint": "NUMBER(38,0)",
        "bigint": "NUMBER(38,0)",
        "serial": "NUMBER(38,0)",
        "bigserial": "NUMBER(38,0)",
        "text": "VARCHAR",
        "boolean": "BOOLEAN",
        "bool": "BOOLEAN",
        "float": "FLOAT",
        "double": "FLOAT",
        "real": "FLOAT",
        "date": "DATE",
        "time": "TIME",
        "timestamp": "TIMESTAMP_NTZ",
        "datetime": "TIMESTAMP_NTZ",
        "timestamptz": "TIMESTAMP_TZ",
        "uuid": "VARCHAR(36)",
        "json": "VARIANT",
        "jsonb": "VARIANT",
        "bytea": "BINARY",
    }

    def map_type(self, column: ParsedColumn) -> str:
        """Ánh xạ kiểu DBML sang kiểu dữ liệu Snowflake."""
        base, args = self.split_type(column.raw_type)
        if self.is_enum_type(column.raw_type):
            return self.default_varchar([])
        if base in self._SIMPLE_TYPES:
            return self._SIMPLE_TYPES[base]
        if base in {"varchar", "character varying", "string"}:
            return self.default_varchar(args)
        if base == "char":
            return self.sized_type("CHAR", args, 1)
        if base in {"decimal", "numeric"}:
            return self.sized_type("NUMBER", args)
        return self.fallback_type(column.raw_type)

    def emit_identity_clause(self) -> str:
        """Snowflake dùng từ khóa AUTOINCREMENT cho cột tự tăng."""
        return "AUTOINCREMENT"

    def emit_create_schema(self) -> str:
        """Sinh câu lệnh tạo schema cách ly Sandbox."""
        return f"CREATE SCHEMA IF NOT EXISTS {self.quote(self._schema_name)};"

    def emit_create_table_header(self, table: ParsedTable) -> str:
        """Sinh dòng mở đầu câu lệnh tạo bảng của Snowflake."""
        return f"CREATE OR REPLACE TABLE {self.qualified_name(table.name)}"
