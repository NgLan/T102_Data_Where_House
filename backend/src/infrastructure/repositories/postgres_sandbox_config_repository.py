"""Triển khai PostgreSQL Repository cho thực thể SandboxConfig."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.sandbox.entities import SandboxConfig
from src.domain.sandbox.i_sandbox_config_repository import ISandboxConfigRepository
from src.domain.shared.types import EntityID
from src.infrastructure.database.error_translation import translate_database_errors
from src.infrastructure.database.mappers.sandbox_config_mapper import SandboxConfigMapper
from src.infrastructure.database.models.sandbox_config import SandboxConfigModel
from src.infrastructure.repositories.sqlalchemy_crud import SqlAlchemyCrud
from src.infrastructure.security.credential_cipher import CredentialCipher
from typing_extensions import override


class PostgresSandboxConfigRepository(ISandboxConfigRepository):
    """Triển khai ISandboxConfigRepository dùng AsyncSession."""

    def __init__(self, session: AsyncSession, credential_cipher: CredentialCipher) -> None:
        """Khởi tạo repository với SQLAlchemy AsyncSession."""
        self._session: AsyncSession = session
        self._mapper = SandboxConfigMapper(credential_cipher)
        self._crud = SqlAlchemyCrud(session, SandboxConfigModel, self._mapper)

    @override
    @translate_database_errors
    async def get_by_project_id(self, project_id: UUID) -> SandboxConfig | None:
        """Lấy cấu hình Sandbox theo ID dự án."""
        stmt = select(SandboxConfigModel).where(SandboxConfigModel.project_id == project_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._mapper.to_domain(model) if model else None

    @override
    async def get_by_id(self, entity_id: EntityID) -> SandboxConfig | None:
        """Lấy cấu hình Sandbox theo ID."""
        return await self._crud.get_by_id(entity_id)

    @override
    @translate_database_errors
    async def save(self, config: SandboxConfig) -> SandboxConfig:
        """Lưu hoặc cập nhật thực thể SandboxConfig."""
        stmt = select(SandboxConfigModel).where(SandboxConfigModel.project_id == config.project_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            model = self._mapper.to_model(config)
            self._session.add(model)
        else:
            self._mapper.update_model(model, config)

        await self._session.flush()
        return self._mapper.to_domain(model, config.password)

    @override
    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa cấu hình Sandbox theo ID."""
        return await self._crud.delete(entity_id)
