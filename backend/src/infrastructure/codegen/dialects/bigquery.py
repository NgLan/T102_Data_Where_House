"""Bộ sinh mã DDL cho Google BigQuery."""

from src.domain.data_model.enums import SqlDialect
from src.infrastructure.codegen.ast import ParsedColumn, ParsedTable
from src.infrastructure.codegen.dialects.base import BaseDialectEmitter


class BigqueryEmitter(BaseDialectEmitter):
    """Sinh script DDL tương thích BigQuery Standard SQL.

    BigQuery không hỗ trợ cột tự tăng và không hỗ trợ CREATE INDEX; ràng buộc khóa chính
    và khóa ngoại phải khai báo inline kèm hậu tố NOT ENFORCED. Khai báo `indexes` của DBML
    được chuyển thành mệnh đề CLUSTER BY.
    """

    dialect: SqlDialect = SqlDialect.BIGQUERY
    quote_char: str = "`"
    supports_increment: bool = False
    supports_index: bool = False
    supports_enum_type: bool = False
    supports_unique_constraint: bool = False
    inline_foreign_key: bool = True

    _MAX_CLUSTER_COLUMNS: int = 4

    _SIMPLE_TYPES: dict[str, str] = {
        "int": "INT64",
        "integer": "INT64",
        "int4": "INT64",
        "int8": "INT64",
        "smallint": "INT64",
        "bigint": "INT64",
        "serial": "INT64",
        "bigserial": "INT64",
        "text": "STRING",
        "varchar": "STRING",
        "character varying": "STRING",
        "string": "STRING",
        "char": "STRING",
        "boolean": "BOOL",
        "bool": "BOOL",
        "float": "FLOAT64",
        "double": "FLOAT64",
        "real": "FLOAT64",
        "date": "DATE",
        "time": "TIME",
        "timestamp": "TIMESTAMP",
        "datetime": "DATETIME",
        "timestamptz": "TIMESTAMP",
        "uuid": "STRING",
        "json": "JSON",
        "jsonb": "JSON",
        "bytea": "BYTES",
    }

    def map_type(self, column: ParsedColumn) -> str:
        """Ánh xạ kiểu DBML sang kiểu dữ liệu BigQuery."""
        base, args = self.split_type(column.raw_type)
        if self.is_enum_type(column.raw_type):
            return "STRING"
        if base in self._SIMPLE_TYPES:
            return self._SIMPLE_TYPES[base]
        if base in {"decimal", "numeric"}:
            return self.sized_type("NUMERIC", args)
        return self.fallback_type(column.raw_type)

    def fallback_type(self, raw_type: str) -> str:
        """BigQuery không có kiểu TEXT, dùng STRING làm kiểu thay thế."""
        self._warnings.append(
            f"Kiểu dữ liệu '{raw_type}' chưa được hỗ trợ cho {self.dialect.value}, "
            "đã tạm ánh xạ thành STRING."
        )
        return "STRING"

    def emit_primary_key_constraint(self, table: ParsedTable) -> str:
        """BigQuery yêu cầu khóa chính khai báo kèm hậu tố NOT ENFORCED."""
        columns = ", ".join(self.quote(name) for name in table.primary_key_columns)
        return f"PRIMARY KEY ({columns}) NOT ENFORCED"

    def emit_inline_foreign_keys(self, table: ParsedTable) -> list[str]:
        """Sinh ràng buộc khóa ngoại inline kèm hậu tố NOT ENFORCED."""
        constraints: list[str] = []
        for ref in self._schema.refs:
            if ref.from_table.lower() != table.name.lower():
                continue
            constraint = self.quote(f"fk_{ref.from_table}_{ref.from_column}".lower())
            constraints.append(
                f"CONSTRAINT {constraint} FOREIGN KEY ({self.quote(ref.from_column)}) "
                f"REFERENCES {self.qualified_name(ref.to_table)} "
                f"({self.quote(ref.to_column)}) NOT ENFORCED"
            )
        return constraints

    def emit_table_options(self, table: ParsedTable) -> str:
        """Chuyển khai báo `indexes` của DBML thành mệnh đề CLUSTER BY của BigQuery."""
        if not table.indexes:
            return ""
        columns: list[str] = []
        for index in table.indexes:
            for name in index.columns:
                if name not in columns:
                    columns.append(name)
        if len(columns) > self._MAX_CLUSTER_COLUMNS:
            self._warnings.append(
                f"BigQuery chỉ cho phép tối đa {self._MAX_CLUSTER_COLUMNS} cột CLUSTER BY, "
                f"bảng '{table.name}' đã bị cắt bớt."
            )
            columns = columns[: self._MAX_CLUSTER_COLUMNS]
        clustered = ", ".join(self.quote(name) for name in columns)
        return f"\nCLUSTER BY {clustered}"

    def emit_create_schema(self) -> str:
        """Sinh câu lệnh tạo dataset cách ly Sandbox."""
        return f"CREATE SCHEMA IF NOT EXISTS {self.quote(self._schema_name)};"

    def emit_create_table_header(self, table: ParsedTable) -> str:
        """Sinh dòng mở đầu câu lệnh tạo bảng của BigQuery."""
        return f"CREATE OR REPLACE TABLE {self.qualified_name(table.name)}"

    def qualified_name(self, table_name: str) -> str:
        """BigQuery bọc trọn `dataset.table` trong một cặp dấu backtick duy nhất."""
        return f"`{self._schema_name}.{table_name}`"
