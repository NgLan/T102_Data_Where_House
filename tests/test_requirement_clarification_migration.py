"""Forward-only migration contracts for Requirement clarification."""

from pathlib import Path

MIGRATION = Path("backend/migrations/20260824_add_requirement_clarification.sql")


def test_migration_backfills_revisions_and_session_purpose() -> None:
    sql = MIGRATION.read_text(encoding="utf-8")

    assert "confirmed_requirement_revision = analyzed_requirement_revision" in sql
    assert "derived_analytical_requirement_revision = analyzed_requirement_revision" in sql
    assert "DEFAULT 'DATA_MODELING'" in sql
    assert "idx_project_sessions_project_purpose_status" in sql
    assert "uq_project_active_requirement_session" in sql
    assert "WHERE purpose = 'REQUIREMENT_CLARIFICATION' AND status = 'ACTIVE'" in sql


def test_migration_creates_case_insensitive_requirement_file_uniqueness() -> None:
    sql = MIGRATION.read_text(encoding="utf-8")

    assert "CREATE TABLE IF NOT EXISTS requirement_files" in sql
    assert "idx_requirement_files_project" in sql
    assert "ON requirement_files (project_id, LOWER(name))" in sql
