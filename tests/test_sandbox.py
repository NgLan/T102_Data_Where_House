"""Unit tests cho UC9.1 và UC9.2 không phụ thuộc PostgreSQL localhost."""

from pathlib import Path
from uuid import uuid4

import pytest
from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.sandbox.input import (
    ExecuteSandboxDdlInput,
    GetSandboxConfigInput,
    SandboxConnectionInput,
    SaveSandboxConfigInput,
)
from src.application.sandbox.input import (
    TestSandboxConnectionInput as SandboxConnectionTestInput,
)
from src.application.sandbox.sandbox_service import SandboxService
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.project.entities import Project, ProjectMember
from src.domain.sandbox.entities import SandboxConfig
from src.domain.sandbox.enums import SandboxDbType
from src.infrastructure.repositories.postgres_sandbox_config_repository import (
    PostgresSandboxConfigRepository,
)
from src.infrastructure.sandbox import sandbox_executor
from src.infrastructure.sandbox.sandbox_executor import (
    PostgresSandboxExecutor,
    check_sandbox_connection,
    execute_sandbox_ddl,
    split_ddl_statements,
)
from src.infrastructure.security.credential_cipher import CredentialCipher

from tests.fakes import (
    FakeProjectMemberRepository,
    FakeProjectRepository,
)


def test_forward_migration_drops_unused_sandbox_status() -> None:
    migration = Path("backend/migrations/20260819_drop_sandbox_config_status.sql")
    sql = migration.read_text(encoding="utf-8").upper()
    assert "DROP COLUMN IF EXISTS STATUS" in sql


def build_sandbox_service(
    repository,
    unit_of_work,
    project: Project,
    actor_id,
    members: list[ProjectMember] | None = None,
) -> SandboxService:
    return SandboxService(
        configs=repository,
        unit_of_work=unit_of_work,
        executor=PostgresSandboxExecutor(),
        access=ProjectAccessPolicy(
            FakeProjectRepository([project]),
            FakeProjectMemberRepository(members or []),
            actor_id,
        ),
    )


class MockSandboxRepository:
    """In-memory repository cho application service tests."""

    def __init__(self) -> None:
        self.store: dict[str, SandboxConfig] = {}

    async def get_by_project_id(self, project_id):
        return self.store.get(str(project_id))

    async def save(self, config):
        self.store[str(config.project_id)] = config
        return config

    async def get_by_id(self, entity_id):
        return next((item for item in self.store.values() if item.id == entity_id), None)

    async def delete(self, entity_id):
        config = await self.get_by_id(entity_id)
        if config is None:
            return False
        self.store.pop(str(config.project_id))
        return True


class MockUnitOfWork:
    """Theo dõi commit mà không mở transaction thật."""

    def __init__(self) -> None:
        self.commit_count = 0

    async def commit(self) -> None:
        self.commit_count += 1

    async def rollback(self) -> None:
        return None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        if exc_type is not None:
            await self.rollback()


class FakeTransaction:
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False

    async def start(self) -> None:
        return None

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


class FakeConnection:
    def __init__(self, failing_fragment: str | None = None) -> None:
        self.failing_fragment = failing_fragment
        self.executed: list[str] = []
        self.closed = False
        self.tx = FakeTransaction()

    def transaction(self) -> FakeTransaction:
        return self.tx

    async def execute(self, statement: str) -> None:
        self.executed.append(statement)
        if self.failing_fragment and self.failing_fragment in statement:
            raise sandbox_executor.asyncpg.PostgresError("synthetic SQL failure")

    async def close(self) -> None:
        self.closed = True


class FakeScalarResult:
    def scalar_one_or_none(self):
        return None


class FakeSession:
    def __init__(self) -> None:
        self.added = None

    async def execute(self, _statement):
        return FakeScalarResult()

    def add(self, model) -> None:
        self.added = model

    async def flush(self) -> None:
        return None


def install_fake_connection(monkeypatch, connection: FakeConnection) -> None:
    async def fake_connect(**_kwargs):
        return connection

    monkeypatch.setattr(sandbox_executor.asyncpg, "connect", fake_connect)


def test_split_ddl_statements_uses_parser_and_rejects_dml():
    ddl = """
    -- dấu ; trong comment không tạo statement
    CREATE TABLE users (id INT, note TEXT DEFAULT 'a;b');
    CREATE TABLE orders (id INT, user_id INT);
    """
    statements = split_ddl_statements(ddl)
    assert len(statements) == 2
    assert "CREATE TABLE users" in statements[0]
    with pytest.raises(ValueError, match="Chỉ cho phép câu lệnh DDL"):
        split_ddl_statements("INSERT INTO users VALUES (1)")


def test_ddl_scope_blocks_privileged_and_cross_schema_statements():
    with pytest.raises(ValueError, match="không được phép trong Sandbox"):
        split_ddl_statements("DROP SCHEMA public CASCADE", allowed_schema="public")
    with pytest.raises(ValueError, match="schema 'sandbox'"):
        split_ddl_statements(
            "CREATE TABLE public.users (id INT)",
            allowed_schema="sandbox",
        )


def test_ddl_scope_allows_generated_postgresql_enum_in_target_schema():
    statements = split_ddl_statements(
        "CREATE TYPE sandbox.role AS ENUM ('admin', 'member')",
        allowed_schema="sandbox",
    )
    assert statements == ["CREATE TYPE sandbox.role AS ENUM ('admin', 'member')"]


@pytest.mark.asyncio
async def test_sandbox_connection_executor_success(monkeypatch):
    connection = FakeConnection()
    install_fake_connection(monkeypatch, connection)
    request = SandboxConnectionInput(
        db_type=SandboxDbType.POSTGRESQL,
        host="localhost",
        port=5432,
        database_name="test_db",
    )
    success, message, latency = await check_sandbox_connection(request)
    assert success is True
    assert "thành công" in message
    assert latency >= 0
    assert connection.closed is True


@pytest.mark.asyncio
async def test_execute_sandbox_ddl_commits_all_statements(monkeypatch):
    connection = FakeConnection()
    install_fake_connection(monkeypatch, connection)
    config = SandboxConfig(project_id=uuid4(), db_type=SandboxDbType.POSTGRESQL)
    ddl = "CREATE TABLE test_table (id INT); ALTER TABLE test_table ADD COLUMN name TEXT;"

    result = await execute_sandbox_ddl(config, ddl)
    assert result.success is True
    assert result.executed_statements == 2
    assert result.succeeded_statements == 2
    assert connection.tx.committed is True
    assert connection.closed is True


@pytest.mark.asyncio
async def test_execute_sandbox_ddl_reports_connection_failure(monkeypatch):
    async def refused_connection(**_kwargs):
        raise OSError("connection refused")

    monkeypatch.setattr(sandbox_executor.asyncpg, "connect", refused_connection)
    config = SandboxConfig(project_id=uuid4(), db_type=SandboxDbType.POSTGRESQL)
    result = await execute_sandbox_ddl(config, "CREATE TABLE unreachable (id INT);")
    assert result.success is False
    assert result.executed_statements == 0
    assert result.succeeded_statements == 0
    assert result.logs[0].statement == "[connection]"


@pytest.mark.asyncio
async def test_execute_sandbox_ddl_rolls_back_on_statement_error(monkeypatch):
    connection = FakeConnection(failing_fragment="bad_table")
    install_fake_connection(monkeypatch, connection)
    config = SandboxConfig(project_id=uuid4(), db_type=SandboxDbType.POSTGRESQL)
    result = await execute_sandbox_ddl(
        config,
        "CREATE TABLE good_table (id INT); CREATE TABLE bad_table (id INT);",
    )
    assert result.success is False
    assert result.succeeded_statements == 0
    assert result.failed_statements == 2
    assert connection.tx.rolled_back is True
    assert "rollback" in (result.logs[0].error_detail or "")


@pytest.mark.asyncio
async def test_sandbox_config_service_commits_and_reads_config():
    repository = MockSandboxRepository()
    unit_of_work = MockUnitOfWork()
    project_id = uuid4()
    owner_id = uuid4()
    project = Project(
        name="Demo", requirement="Design data warehouse", user_id=owner_id, id=project_id
    )
    service = build_sandbox_service(repository, unit_of_work, project, owner_id)
    assert await service.get_config(GetSandboxConfigInput(project_id)) is None

    response = await service.save_config(
        SaveSandboxConfigInput(
            project_id,
            SandboxConnectionInput(
            host="127.0.0.1",
            port=5433,
            database_name="sandbox_dwh",
            username="admin",
            password="secretpassword",
            schema_name="public",
            db_type=SandboxDbType.POSTGRESQL,
            ),
        )
    )
    assert response.host == "127.0.0.1"
    assert response.database_name == "sandbox_dwh"
    assert unit_of_work.commit_count == 1
    assert (await service.get_config(GetSandboxConfigInput(project_id))).id == response.id


@pytest.mark.asyncio
async def test_execute_ddl_service_requires_saved_config(monkeypatch):
    repository = MockSandboxRepository()
    project_id = uuid4()
    owner_id = uuid4()
    project = Project(
        name="Demo", requirement="Design data warehouse", user_id=owner_id, id=project_id
    )
    service = build_sandbox_service(repository, MockUnitOfWork(), project, owner_id)
    request = ExecuteSandboxDdlInput(project_id, "CREATE TABLE dim_customer (id INT);")
    with pytest.raises(BusinessException) as exc_info:
        await service.execute_ddl(request)
    assert exc_info.value.code.value == "SANDBOX_CONFIG_NOT_FOUND"

    await repository.save(SandboxConfig(project_id=project_id))
    install_fake_connection(monkeypatch, FakeConnection())
    response = await service.execute_ddl(request)
    assert response.success is True
    assert response.succeeded_statements == 1


@pytest.mark.asyncio
async def test_sandbox_member_can_read_but_cannot_save_config():
    repository = MockSandboxRepository()
    owner_id, member_id, project_id = uuid4(), uuid4(), uuid4()
    project = Project(
        id=project_id,
        name="Demo",
        requirement="Design data warehouse",
        user_id=owner_id,
    )
    member = ProjectMember(project_id=project_id, user_id=member_id)
    await repository.save(SandboxConfig(project_id=project_id))
    service = build_sandbox_service(
        repository,
        MockUnitOfWork(),
        project,
        member_id,
        [member],
    )

    assert await service.get_config(GetSandboxConfigInput(project_id)) is not None
    with pytest.raises(BusinessException) as exc_info:
        await service.save_config(
            SaveSandboxConfigInput(project_id, SandboxConnectionInput(SandboxDbType.POSTGRESQL, "localhost", 5432, "db"))
        )
    assert exc_info.value.code == ErrorCode.PERMISSION_DENIED


@pytest.mark.asyncio
async def test_sandbox_test_connection_requires_owner():
    owner_id, member_id, project_id = uuid4(), uuid4(), uuid4()
    project = Project(
        id=project_id,
        name="Demo",
        requirement="Design data warehouse",
        user_id=owner_id,
    )
    member = ProjectMember(project_id=project_id, user_id=member_id)
    service = build_sandbox_service(
        MockSandboxRepository(),
        MockUnitOfWork(),
        project,
        member_id,
        [member],
    )

    with pytest.raises(BusinessException) as exc_info:
        await service.test_connection(
            SandboxConnectionTestInput(
                project_id,
                SandboxConnectionInput(
                    SandboxDbType.POSTGRESQL,
                    "localhost",
                    5432,
                    "sandbox",
                ),
            )
        )
    assert exc_info.value.code == ErrorCode.PERMISSION_DENIED


def test_credential_cipher_does_not_store_plaintext():
    cipher = CredentialCipher("test-secret-key")
    encrypted = cipher.encrypt("database-password")
    assert encrypted is not None
    assert "database-password" not in encrypted
    assert cipher.decrypt(encrypted) == "database-password"


def test_credential_cipher_keeps_legacy_plaintext_and_translates_invalid_token():
    cipher = CredentialCipher("test-secret-key")
    assert cipher.decrypt("legacy-password") == "legacy-password"

    with pytest.raises(InfrastructureException) as exc_info:
        cipher.decrypt("fernet:not-a-token")

    assert exc_info.value.code == ErrorCode.STORAGE_ERROR


@pytest.mark.asyncio
async def test_postgres_repository_sets_timestamps_and_encrypts_password():
    session = FakeSession()
    cipher = CredentialCipher("test-secret-key")
    repository = PostgresSandboxConfigRepository(session, cipher)
    config = SandboxConfig(project_id=uuid4(), password="database-password")

    saved = await repository.save(config)

    assert session.added.created_at == config.created_at
    assert session.added.updated_at == config.updated_at
    assert session.added.password.startswith("fernet:")
    assert "database-password" not in session.added.password
    assert saved.password == "database-password"
