"""Forward-only auth migration contract for legacy and fresh databases."""

from pathlib import Path

MIGRATION = Path(__file__).parents[3] / "migrations" / "20260823_add_jwt_auth.sql"


def test_auth_migration_preserves_legacy_users_without_credentials() -> None:
    sql = MIGRATION.read_text(encoding="utf-8").upper()

    assert "ADD COLUMN IF NOT EXISTS PASSWORD_HASH" in sql
    assert "IS_ACTIVE BOOLEAN NOT NULL DEFAULT FALSE" in sql
    assert "LOWER(USERNAME)" in sql
    assert "LOWER(EMAIL)" in sql


def test_auth_migration_persists_token_revocation() -> None:
    sql = MIGRATION.read_text(encoding="utf-8").upper()

    assert "CREATE TABLE IF NOT EXISTS REVOKED_AUTH_TOKENS" in sql
    assert "JTI VARCHAR(64) NOT NULL UNIQUE" in sql
    assert "REFERENCES USERS(ID) ON DELETE CASCADE" in sql
    assert "EXPIRES_AT TIMESTAMPTZ NOT NULL" in sql
