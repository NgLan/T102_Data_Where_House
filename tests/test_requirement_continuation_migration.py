"""Forward-only migration contract cho Requirement continuation gate."""

from pathlib import Path

MIGRATION = Path("backend/migrations/20260826_add_requirement_continuation_state.sql")


def test_migration_backfills_requirement_continuation_state() -> None:
    sql = MIGRATION.read_text(encoding="utf-8")

    assert "ADD COLUMN IF NOT EXISTS requirement_continuation_state" in sql
    assert "SET requirement_continuation_state = 'NOT_REQUIRED'" in sql
    assert "SET DEFAULT 'NOT_REQUIRED'" in sql
    assert "SET NOT NULL" in sql
