"""Forward-only persistence contract for Source Coverage state."""

from pathlib import Path

MIGRATION = Path(__file__).parents[3] / "migrations" / "20260826_add_source_coverage.sql"


def test_source_coverage_migration_adds_typed_state_without_destructive_sql() -> None:
    sql = MIGRATION.read_text(encoding="utf-8").upper()
    assert "SOURCE_COVERAGE JSONB NOT NULL DEFAULT '[]'::JSONB" in sql
    assert "COVERED_ANALYTICAL_REQUIREMENT_REVISION INTEGER NOT NULL DEFAULT 0" in sql
    assert "DROP COLUMN" not in sql
