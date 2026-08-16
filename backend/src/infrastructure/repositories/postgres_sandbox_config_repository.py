"""Triển khai PostgreSQL Repository cho thực thể SandboxConfig."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.sandbox.enums import SandboxDbType
from src.domain.sandbox.repository import ISandboxConfigRepository
from src.domain.sandbox.sandbox import SandboxConfig
from src.infrastructure.database.models.sandbox_config import SandboxConfigModel
from src.infrastructure.security.credential_cipher import CredentialCipher
from typing_extensions import override


class PostgresSandboxConfigRepository(ISandboxConfigRepository):
    """Triển khai ISandboxConfigRepository dùng AsyncSession."""

    def __init__(self, session: AsyncSession, credential_cipher: CredentialCipher) -> None:
        """Khởi tạo repository với SQLAlchemy AsyncSession."""
        self._session: AsyncSession = session
        self._credential_cipher = credential_cipher

    @override
    async def get_by_project_id(self, project_id: UUID) -> SandboxConfig | None:
        """Lấy cấu hình Sandbox theo ID dự án."""
        stmt = select(SandboxConfigModel).where(SandboxConfigModel.project_id == project_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return SandboxConfig(
            id=model.id,
            project_id=model.project_id,
            db_type=SandboxDbType(model.db_type),
            host=model.host,
            port=model.port,
            database_name=model.database_name,
            username=model.username,
            password=self._credential_cipher.decrypt(model.password),
            schema_name=model.schema_name,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @override
    async def save(self, config: SandboxConfig) -> SandboxConfig:
        """Lưu hoặc cập nhật thực thể SandboxConfig."""
        stmt = select(SandboxConfigModel).where(SandboxConfigModel.project_id == config.project_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            model.db_type = config.db_type.value
            model.host = config.host
            model.port = config.port
            model.database_name = config.database_name
            model.username = config.username
            model.password = self._credential_cipher.encrypt(config.password)
            model.schema_name = config.schema_name
            model.updated_at = config.updated_at
        else:
            model = SandboxConfigModel(
                id=config.id,
                project_id=config.project_id,
                db_type=config.db_type.value,
                host=config.host,
                port=config.port,
                database_name=config.database_name,
                username=config.username,
                password=self._credential_cipher.encrypt(config.password),
                schema_name=config.schema_name,
                created_at=config.created_at,
                updated_at=config.updated_at,
            )
            self._session.add(model)

        await self._session.flush()
        return SandboxConfig(
            id=model.id,
            project_id=model.project_id,
            db_type=SandboxDbType(model.db_type),
            host=model.host,
            port=model.port,
            database_name=model.database_name,
            username=model.username,
            password=config.password,
            schema_name=model.schema_name,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
