"""Contract tests cho migration metadata cột sang schema typed mới."""

from pathlib import Path

MIGRATION = (
    Path(__file__).parents[1]
    / "backend"
    / "migrations"
    / "20260822_normalize_data_source_column_metadata.sql"
)


def test_migration_maps_legacy_metadata_and_removes_old_keys() -> None:
    """Migration phải giữ dữ liệu trước khi runtime decoder chuyển sang strict schema."""
    sql = MIGRATION.read_text(encoding="utf-8")

    assert "'CATEGORY'" in sql
    assert "'distinct_values'" in sql
    assert "'FOREIGN_KEY'" in sql
    assert "'UNIQUE'" in sql
    assert "'CHECK'" in sql
    assert "'DEFAULT'" in sql
    assert "- 'semantic_type'" in sql
    assert "- 'sample_values'" in sql
    assert "- 'options'" in sql
