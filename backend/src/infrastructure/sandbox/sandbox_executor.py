"""Driver adapter kiểm tra kết nối và thực thi PostgreSQL DDL thật."""

import re
import time
from typing import Any

try:
    import asyncpg
except ImportError:
    asyncpg = None  # type: ignore[assignment]

try:
    from sqlglot import exp, parse
    from sqlglot.errors import ParseError
except ImportError:
    exp = None  # type: ignore
    parse = None  # type: ignore
    ParseError = Exception  # type: ignore
from src.common.logging import get_logger
from src.common.utils.datetime import to_isoformat, utc_now
from src.domain.sandbox.enums import SandboxDbType
from src.domain.sandbox.sandbox import SandboxConfig, SandboxExecutionResult, StatementLog

logger = get_logger(__name__)
SCHEMA_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
ALLOWED_DDL_EXPRESSIONS = (exp.Create, exp.Alter, exp.Drop, exp.Comment) if exp else ()
ALLOWED_DDL_KINDS = {"INDEX", "SEQUENCE", "TABLE", "VIEW"}
ALLOWED_COMMENT_KINDS = {"COLUMN", "TABLE", "VIEW"}
ENUM_VALUE_PATTERN = r"'(?:''|[^'])*'"
IDENTIFIER_PATTERN = r'(?:"(?:[^"]|"")*"|[A-Za-z_][A-Za-z0-9_]*)'
CREATE_ENUM_PATTERN = re.compile(
    rf"^CREATE\s+TYPE\s+"
    rf"(?:(?P<schema>{IDENTIFIER_PATTERN})\s*\.\s*)?{IDENTIFIER_PATTERN}"
    rf"\s+AS\s+ENUM\s*\(\s*{ENUM_VALUE_PATTERN}"
    rf"(?:\s*,\s*{ENUM_VALUE_PATTERN})*\s*\)$",
    re.IGNORECASE | re.DOTALL,
)


def split_ddl_statements(ddl_script: str, allowed_schema: str | None = None) -> list[str]:
    """Parse PostgreSQL script thành statement DDL."""
    if parse is None:
        cleaned = re.sub(r"--.*?\n", "\n", ddl_script)
        cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL)
        return [stmt.strip() for stmt in cleaned.split(";") if stmt.strip()]

    try:
        expressions = parse(ddl_script, read="postgres")
    except ParseError as exc:
        raise ValueError(f"DDL không hợp lệ: {exc}") from exc
    statements: list[str] = []
    for expression in expressions:
        if expression is None:
            continue
        if isinstance(expression, exp.Command):
            statement = expression.sql(dialect="postgres").strip()
            _validate_safe_command(statement, allowed_schema)
            statements.append(statement)
            continue
        if not isinstance(expression, ALLOWED_DDL_EXPRESSIONS):
            raise ValueError(f"Chỉ cho phép câu lệnh DDL; nhận được {type(expression).__name__}.")
        _validate_expression_scope(expression, allowed_schema)
        statements.append(expression.sql(dialect="postgres"))
    return statements


def _validate_expression_scope(expression: Any, allowed_schema: str | None) -> None:
    """Chỉ cho phép DDL cục bộ trên các đối tượng an toàn của schema Sandbox."""
    kind = str(expression.args.get("kind") or "").upper()
    if isinstance(expression, exp.Comment):
        if kind not in ALLOWED_COMMENT_KINDS:
            raise ValueError(f"COMMENT ON {kind or 'UNKNOWN'} không được phép trong Sandbox.")
    elif kind not in ALLOWED_DDL_KINDS:
        raise ValueError(f"DDL trên đối tượng {kind or 'UNKNOWN'} không được phép trong Sandbox.")

    if not allowed_schema:
        return
    normalized_schema = allowed_schema.casefold()
    for relation in expression.find_all(exp.Table):
        _validate_namespace(relation.catalog, relation.db, normalized_schema, allowed_schema)
    for column in expression.find_all(exp.Column):
        _validate_namespace(column.catalog, column.db, normalized_schema, allowed_schema)


def _validate_namespace(catalog: str, schema: str, normalized_schema: str, allowed_schema: str) -> None:
    if catalog:
        raise ValueError("DDL không được tham chiếu database/catalog khác.")
    if schema and schema.casefold() != normalized_schema:
        raise ValueError(f"DDL chỉ được thao tác trong schema '{allowed_schema}'.")


def _validate_safe_command(statement: str, allowed_schema: str | None) -> None:
    """Chỉ chấp nhận CREATE TYPE ... AS ENUM do sqlglot chưa parse được."""
    match = CREATE_ENUM_PATTERN.fullmatch(statement)
    if match is None:
        raise ValueError("Câu lệnh DDL này chưa được hỗ trợ trong Sandbox.")
    schema = match.group("schema")
    if schema and allowed_schema and _unquote_identifier(schema).casefold() != allowed_schema.casefold():
        raise ValueError(f"DDL chỉ được thao tác trong schema '{allowed_schema}'.")


def _unquote_identifier(identifier: str) -> str:
    if identifier.startswith('"') and identifier.endswith('"'):
        return identifier[1:-1].replace('""', '"')
    return identifier


async def check_sandbox_connection(config: Any) -> tuple[bool, str, float]:
    """Kết nối thật tới PostgreSQL và không giả lập thành công."""
    start = time.perf_counter()
    if getattr(config, "db_type", SandboxDbType.POSTGRESQL) != SandboxDbType.POSTGRESQL:
        elapsed = (time.perf_counter() - start) * 1000
        return False, "Hiện tại chỉ hỗ trợ PostgreSQL Sandbox.", round(elapsed, 2)
    if asyncpg is None:
        elapsed = (time.perf_counter() - start) * 1000
        return False, "Backend chưa cài đặt asyncpg.", round(elapsed, 2)
    try:
        conn = await asyncpg.connect(
            user=getattr(config, "username", "postgres") or "postgres",
            password=getattr(config, "password", "") or "",
            database=getattr(config, "database_name", "postgres") or "postgres",
            host=getattr(config, "host", "localhost") or "localhost",
            port=getattr(config, "port", 5432) or 5432,
            timeout=5.0,
        )
        await conn.close()
        elapsed = (time.perf_counter() - start) * 1000
        return True, "Kết nối thành công đến PostgreSQL Sandbox Database!", round(elapsed, 2)
    except Exception as exc:
        elapsed = (time.perf_counter() - start) * 1000
        logger.warning("Lỗi kết nối Sandbox DB: %s", exc)
        return False, f"Không thể kết nối đến Sandbox DB: {exc}", round(elapsed, 2)


async def execute_sandbox_ddl(config: SandboxConfig, ddl_script: str) -> SandboxExecutionResult:
    """Thực thi DDL trong một transaction; rollback toàn bộ khi có lỗi."""
    started_at = time.perf_counter()
    if config.db_type != SandboxDbType.POSTGRESQL:
        return _failed_result("[engine]", "Hiện tại chỉ hỗ trợ PostgreSQL Sandbox.", started_at)
    schema_name = config.schema_name or "public"
    if not SCHEMA_PATTERN.fullmatch(schema_name):
        return _failed_result("[schema]", "Tên schema không hợp lệ.", started_at)
    try:
        statements = split_ddl_statements(ddl_script, allowed_schema=schema_name)
    except ValueError as exc:
        return _failed_result("[validation]", str(exc), started_at)
    if not statements:
        return _failed_result("[validation]", "DDL script không có câu lệnh.", started_at)

    conn, connection_error = await _try_connect_db(config)
    if conn is None:
        return _failed_result("[connection]", connection_error, started_at)

    logs: list[StatementLog] = []
    transaction = conn.transaction()
    try:
        await transaction.start()
        await conn.execute(f'SET LOCAL search_path TO "{schema_name}"')
        await conn.execute("SET LOCAL lock_timeout TO '5s'")
        await conn.execute("SET LOCAL statement_timeout TO '30s'")
        for statement in statements:
            log_entry = await _run_single_statement(conn, statement)
            logs.append(log_entry)
            if not log_entry.is_success:
                await transaction.rollback()
                _mark_rolled_back(logs[:-1])
                return _result_from_logs(logs, started_at, success=False)
        await transaction.commit()
        return _result_from_logs(logs, started_at, success=True)
    except Exception as exc:
        try:
            await transaction.rollback()
        except Exception:
            logger.exception("Không thể rollback transaction Sandbox.")
        _mark_rolled_back(logs)
        logs.append(_error_log("[transaction]", str(exc)))
        return _result_from_logs(logs, started_at, success=False)
    finally:
        await conn.close()


async def _try_connect_db(config: SandboxConfig) -> tuple[Any | None, str]:
    if asyncpg is None:
        return None, "Backend chưa cài đặt asyncpg."
    try:
        connection = await asyncpg.connect(
            user=config.username or "postgres",
            password=config.password or "",
            database=config.database_name,
            host=config.host,
            port=config.port,
            timeout=5.0,
        )
        return connection, ""
    except Exception as exc:
        logger.warning("Kết nối DB Sandbox thất bại: %s", exc)
        return None, f"Không thể kết nối đến Sandbox DB: {exc}"


async def _run_single_statement(conn: Any, statement: str) -> StatementLog:
    started_at = time.perf_counter()
    try:
        await conn.execute(statement)
        duration = (time.perf_counter() - started_at) * 1000
        return StatementLog(
            statement=statement,
            is_success=True,
            execution_time_ms=round(duration, 2),
            timestamp=to_isoformat(utc_now()),
        )
    except Exception as exc:
        duration = (time.perf_counter() - started_at) * 1000
        return StatementLog(
            statement=statement,
            is_success=False,
            execution_time_ms=round(duration, 2),
            timestamp=to_isoformat(utc_now()),
            error_detail=str(exc),
        )


def _mark_rolled_back(logs: list[StatementLog]) -> None:
    for log in logs:
        log.is_success = False
        log.error_detail = "Đã rollback vì một câu lệnh khác thất bại."


def _error_log(statement: str, detail: str) -> StatementLog:
    return StatementLog(
        statement=statement,
        is_success=False,
        execution_time_ms=0,
        timestamp=to_isoformat(utc_now()),
        error_detail=detail,
    )


def _failed_result(statement: str, detail: str, started_at: float) -> SandboxExecutionResult:
    duration = (time.perf_counter() - started_at) * 1000
    return SandboxExecutionResult(
        success=False,
        executed_statements=0,
        succeeded_statements=0,
        failed_statements=0,
        total_duration_ms=round(duration, 2),
        logs=[_error_log(statement, detail)],
    )


def _result_from_logs(logs: list[StatementLog], started_at: float, success: bool) -> SandboxExecutionResult:
    duration = (time.perf_counter() - started_at) * 1000
    succeeded = sum(log.is_success for log in logs)
    return SandboxExecutionResult(
        success=success,
        executed_statements=len(logs),
        succeeded_statements=succeeded,
        failed_statements=len(logs) - succeeded,
        total_duration_ms=round(duration, 2),
        logs=logs,
    )
