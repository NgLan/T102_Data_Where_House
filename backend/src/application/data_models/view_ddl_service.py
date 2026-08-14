"""Use case sinh mã DDL từ mô hình dữ liệu hiện tại."""

import re
from collections.abc import Callable

from src.common.exceptions import BusinessException, ErrorCode
from src.common.utils.datetime import to_isoformat, utc_now
from src.domain.data_model.entities import DataModelSnapshot, DdlDocument
from src.domain.data_model.enums import DdlDialect
from src.domain.data_model.value_objects import ColumnDefinition, TableDefinition

TABLE_PATTERN = re.compile(r"Table\s+([A-Za-z_][\w]*)\s*\{([^}]*)}", re.IGNORECASE | re.DOTALL)
COLUMN_PATTERN = re.compile(r"^([A-Za-z_][\w]*)\s+([^\s\[]+)(?:\s+\[([^]]+)])?$")
TYPE_PATTERN = re.compile(r"^([A-Za-z]+)(?:\(([^)]+)\))?$")


class ViewDdlService:
    """Sinh DDL theo dialect từ DBML đang hiển thị trên workspace."""

    def execute(self, model: DataModelSnapshot, dialect: DdlDialect) -> DdlDocument:
        """Sinh tài liệu DDL từ ảnh chụp mô hình hiện tại."""
        tables = self._parse_tables(model.dbml)
        if not tables:
            raise BusinessException(
                code=ErrorCode.INVALID_DATA_MODEL,
                message="Mô hình hiện tại không chứa định nghĩa bảng DBML hợp lệ.",
            )
        statements = [self._render_table(table, dialect) for table in tables]
        return DdlDocument(
            model_name=model.name,
            revision=model.revision,
            dialect=dialect,
            content=self._compose_document(model, dialect, statements),
            table_count=len(tables),
            generated_at=to_isoformat(utc_now()),
        )

    def _parse_tables(self, dbml: str) -> tuple[TableDefinition, ...]:
        """Chuyển các khối Table DBML thành value object."""
        tables: list[TableDefinition] = []
        for match in TABLE_PATTERN.finditer(dbml):
            columns = tuple(self._parse_columns(match.group(2)))
            if columns:
                tables.append(TableDefinition(name=match.group(1), columns=columns))
        return tuple(tables)

    def _parse_columns(self, body: str) -> list[ColumnDefinition]:
        """Đọc các dòng cột trong một khối Table DBML."""
        columns: list[ColumnDefinition] = []
        for raw_line in body.splitlines():
            line = raw_line.split("//", maxsplit=1)[0].strip()
            match = COLUMN_PATTERN.match(line)
            if match:
                columns.append(self._build_column(match))
        return columns

    def _build_column(self, match: re.Match[str]) -> ColumnDefinition:
        """Tạo định nghĩa cột từ kết quả parse."""
        attributes = match.group(3) or ""
        reference_match = re.search(r"ref:\s*>\s*([\w.]+)", attributes, re.IGNORECASE)
        normalized = attributes.lower()
        tokens = {token.strip() for token in normalized.split(",")}
        return ColumnDefinition(
            name=match.group(1),
            data_type=match.group(2),
            primary_key="pk" in tokens,
            nullable="not null" not in normalized,
            increment="increment" in normalized,
            reference=reference_match.group(1) if reference_match else None,
        )

    def _render_table(self, table: TableDefinition, dialect: DdlDialect) -> str:
        """Sinh một câu CREATE TABLE theo dialect."""
        quote = self._quote_factory(dialect)
        lines = [self._render_column(column, dialect, quote) for column in table.columns]
        constraints = self._render_constraints(table, dialect, quote)
        body = ",\n".join(f"  {line}" for line in [*lines, *constraints])
        return f"CREATE TABLE {quote(table.name)} (\n{body}\n);"

    def _render_column(
        self,
        column: ColumnDefinition,
        dialect: DdlDialect,
        quote: Callable[[str], str],
    ) -> str:
        """Sinh khai báo một cột DDL."""
        data_type = self._map_type(column.data_type, dialect)
        identity = self._identity_clause(column, dialect)
        nullable = "" if column.nullable else " NOT NULL"
        return f"{quote(column.name)} {data_type}{identity}{nullable}"

    def _render_constraints(
        self,
        table: TableDefinition,
        dialect: DdlDialect,
        quote: Callable[[str], str],
    ) -> list[str]:
        """Sinh các ràng buộc PK và FK của bảng."""
        constraints: list[str] = []
        primary_keys = [quote(column.name) for column in table.columns if column.primary_key]
        if primary_keys:
            suffix = " NOT ENFORCED" if dialect is DdlDialect.BIGQUERY else ""
            constraints.append(f"PRIMARY KEY ({', '.join(primary_keys)}){suffix}")
        constraints.extend(self._foreign_keys(table, dialect, quote))
        return constraints

    def _foreign_keys(
        self,
        table: TableDefinition,
        dialect: DdlDialect,
        quote: Callable[[str], str],
    ) -> list[str]:
        """Sinh danh sách ràng buộc khóa ngoại."""
        foreign_keys: list[str] = []
        suffix = " NOT ENFORCED" if dialect is DdlDialect.BIGQUERY else ""
        for column in table.columns:
            if not column.reference:
                continue
            target_table, target_column = column.reference.split(".", maxsplit=1)
            foreign_keys.append(
                f"FOREIGN KEY ({quote(column.name)}) REFERENCES "
                f"{quote(target_table)} ({quote(target_column)}){suffix}"
            )
        return foreign_keys

    def _map_type(self, dbml_type: str, dialect: DdlDialect) -> str:
        """Ánh xạ kiểu DBML sang kiểu dữ liệu của dialect."""
        match = TYPE_PATTERN.match(dbml_type)
        if not match:
            return dbml_type.upper()
        base, parameters = match.group(1).lower(), match.group(2)
        mapped = self._type_mapping(dialect).get(base, base.upper())
        if parameters and mapped not in {"STRING", "INT64", "BOOL", "FLOAT64"}:
            return f"{mapped}({parameters})"
        return mapped

    def _type_mapping(self, dialect: DdlDialect) -> dict[str, str]:
        """Trả về bảng ánh xạ kiểu dữ liệu theo dialect."""
        common = {"int": "INTEGER", "integer": "INTEGER", "bigint": "BIGINT"}
        if dialect is DdlDialect.BIGQUERY:
            return {
                **common,
                "int": "INT64",
                "integer": "INT64",
                "bigint": "INT64",
                "varchar": "STRING",
                "decimal": "NUMERIC",
                "boolean": "BOOL",
                "float": "FLOAT64",
            }
        if dialect is DdlDialect.SNOWFLAKE:
            return {
                **common,
                "decimal": "NUMBER",
                "timestamp": "TIMESTAMP_NTZ",
                "boolean": "BOOLEAN",
            }
        return {**common, "decimal": "NUMERIC", "boolean": "BOOLEAN"}

    def _identity_clause(self, column: ColumnDefinition, dialect: DdlDialect) -> str:
        """Sinh cú pháp tự tăng tương ứng nếu cột yêu cầu increment."""
        if not column.increment or dialect is DdlDialect.BIGQUERY:
            return ""
        if dialect is DdlDialect.SNOWFLAKE:
            return " AUTOINCREMENT START 1 INCREMENT 1"
        return " GENERATED BY DEFAULT AS IDENTITY"

    def _quote_factory(self, dialect: DdlDialect) -> Callable[[str], str]:
        """Tạo hàm quote identifier an toàn theo dialect."""
        marker = "`" if dialect is DdlDialect.BIGQUERY else '"'
        return lambda identifier: f"{marker}{identifier}{marker}"

    def _compose_document(
        self,
        model: DataModelSnapshot,
        dialect: DdlDialect,
        statements: list[str],
    ) -> str:
        """Ghép metadata và các câu lệnh thành tài liệu DDL hoàn chỉnh."""
        header = (
            f"-- Model: {model.name}\n"
            f"-- Revision: {model.revision}\n"
            f"-- Dialect: {dialect.value}\n"
            "-- Generated by DataCraft AI\n"
        )
        return f"{header}\n" + "\n\n".join(statements) + "\n"
