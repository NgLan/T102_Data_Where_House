"""Triển khai bộ sinh mã DDL từ nội dung DBML cho nhiều hệ quản trị CSDL."""

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.logging import get_logger
from src.common.utils.datetime import to_isoformat, utc_now
from src.domain.data_model.codegen import DdlGenerationResult, IDdlGenerator
from src.domain.data_model.enums import SqlDialect
from src.infrastructure.codegen.constants import DEFAULT_SANDBOX_SCHEMA
from src.infrastructure.codegen.dbml_parser import parse_dbml
from src.infrastructure.codegen.dialects import EMITTER_REGISTRY, BaseDialectEmitter

logger = get_logger(__name__)

_SECTION_SEPARATOR = "\n\n"


class DbmlDdlGenerator(IDdlGenerator):
    """Biên dịch DBML thành script DDL theo dialect đích (PostgreSQL/Snowflake/BigQuery)."""

    def generate(
        self,
        dbml: str,
        dialect: SqlDialect,
        schema_name: str | None = None,
    ) -> DdlGenerationResult:
        """Biên dịch nội dung DBML thành script DDL của hệ quản trị CSDL đích."""
        emitter_class = EMITTER_REGISTRY.get(dialect)
        if emitter_class is None:
            raise BusinessException(
                code=ErrorCode.INVALID_DATA_MODEL,
                message=f"Hệ quản trị CSDL '{dialect}' chưa được hỗ trợ sinh mã DDL.",
            )

        target_schema = (schema_name or DEFAULT_SANDBOX_SCHEMA).strip() or DEFAULT_SANDBOX_SCHEMA
        schema = parse_dbml(dbml)
        emitter = emitter_class(schema, target_schema)
        ddl = self._render(emitter, dialect, target_schema)

        logger.info(
            "ddl_generation_completed dialect=%s tables=%d warnings=%d",
            dialect.value,
            len(schema.tables),
            len(emitter.warnings),
        )
        return DdlGenerationResult(
            ddl=ddl,
            dialect=dialect,
            schema_name=target_schema,
            table_count=len(schema.tables),
            warnings=emitter.warnings,
        )

    def _render(
        self,
        emitter: BaseDialectEmitter,
        dialect: SqlDialect,
        schema_name: str,
    ) -> str:
        """Ghép các phần của script DDL theo đúng thứ tự thực thi an toàn."""
        tables = emitter.sorted_tables()
        sections: list[str] = [
            self._render_header(dialect, schema_name, len(tables)),
            emitter.emit_create_schema(),
        ]
        sections.extend(emitter.emit_enum_statements())
        sections.extend(emitter.emit_create_table(table) for table in tables)

        foreign_keys = emitter.emit_foreign_key_statements()
        if foreign_keys:
            sections.append("-- Ràng buộc khóa ngoại (Foreign Keys)")
            sections.extend(foreign_keys)

        indexes = emitter.emit_index_statements()
        if indexes:
            sections.append("-- Chỉ mục (Indexes)")
            sections.extend(indexes)

        return _SECTION_SEPARATOR.join(sections) + "\n"

    def _render_header(self, dialect: SqlDialect, schema_name: str, table_count: int) -> str:
        """Sinh khối chú thích mở đầu script DDL."""
        line = "-- " + "=" * 60
        return "\n".join(
            [
                line,
                "-- Data Warehouse DDL sinh tự động từ DBML bởi AI20K Agent System",
                f"-- Hệ quản trị CSDL đích : {dialect.value}",
                f"-- Schema Sandbox        : {schema_name}",
                f"-- Số bảng               : {table_count}",
                f"-- Thời điểm sinh mã     : {to_isoformat(utc_now())}",
                "-- CẢNH BÁO: script này chỉ dành cho môi trường Sandbox, không chạy trên Production.",
                line,
            ]
        )
