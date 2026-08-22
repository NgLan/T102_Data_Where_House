"""Kiểm tra migration chuyển workflow tracking sang revision."""

from pathlib import Path

MIGRATION = Path("backend/migrations/20260821_replace_workflow_fingerprints_with_revisions.sql")


def test_migration_adds_revisions_and_drops_fingerprints() -> None:
    """Migration tiến tới phải tạo revision columns và xóa fingerprint columns."""
    sql = MIGRATION.read_text(encoding="utf-8")
    required_columns = (
        "requirement_revision",
        "source_revision",
        "analyzed_requirement_revision",
        "analyzed_source_revision",
        "generated_from_requirement_revision",
        "generated_from_source_revision",
    )

    assert all(column in sql for column in required_columns)
    assert "base_requirement_revision" not in sql
    assert "base_source_revision" not in sql
    assert "DROP COLUMN IF EXISTS input_fingerprint" in sql
