"""Tập hợp các bộ sinh mã DDL theo từng hệ quản trị CSDL."""

from src.domain.data_model.enums import SqlDialect
from src.infrastructure.codegen.dialects.base import BaseDialectEmitter
from src.infrastructure.codegen.dialects.bigquery import BigqueryEmitter
from src.infrastructure.codegen.dialects.postgresql import PostgresqlEmitter
from src.infrastructure.codegen.dialects.snowflake import SnowflakeEmitter

EMITTER_REGISTRY: dict[SqlDialect, type[BaseDialectEmitter]] = {
    SqlDialect.POSTGRESQL: PostgresqlEmitter,
    SqlDialect.SNOWFLAKE: SnowflakeEmitter,
    SqlDialect.BIGQUERY: BigqueryEmitter,
}

__all__: list[str] = [
    "BaseDialectEmitter",
    "PostgresqlEmitter",
    "SnowflakeEmitter",
    "BigqueryEmitter",
    "EMITTER_REGISTRY",
]
