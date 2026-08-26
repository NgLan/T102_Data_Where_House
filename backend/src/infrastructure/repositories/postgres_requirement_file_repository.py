"""PostgreSQL repository cho RequirementFile."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.requirement_file.entities import RequirementFile
from src.domain.requirement_file.i_requirement_file_repository import (
    IRequirementFileRepository,
)
from src.domain.shared.types import EntityID
from src.infrastructure.database.error_translation import translate_database_errors
from src.infrastructure.database.mappers.requirement_file_mapper import (
    RequirementFileMapper,
)
from src.infrastructure.database.models.requirement_file import RequirementFileModel
from src.infrastructure.repositories.sqlalchemy_crud import SqlAlchemyCrud
from typing_extensions import override


class PostgresRequirementFileRepository(IRequirementFileRepository):
    """Lưu Requirement Documents bằng SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._crud = SqlAlchemyCrud(
            session, RequirementFileModel, RequirementFileMapper
        )

    @override
    async def get_by_id(self, entity_id: EntityID) -> RequirementFile | None:
        return await self._crud.get_by_id(entity_id)

    @override
    @translate_database_errors
    async def list_by_project(self, project_id: EntityID) -> list[RequirementFile]:
        result = await self._session.execute(
            select(RequirementFileModel)
            .where(RequirementFileModel.project_id == project_id)
            .order_by(RequirementFileModel.created_at.asc())
        )
        return [RequirementFileMapper.to_domain(item) for item in result.scalars()]

    @override
    @translate_database_errors
    async def get_by_project_name(
        self, project_id: EntityID, name: str
    ) -> RequirementFile | None:
        result = await self._session.execute(
            select(RequirementFileModel).where(
                RequirementFileModel.project_id == project_id,
                func.lower(RequirementFileModel.name) == name.casefold(),
            )
        )
        model = result.scalar_one_or_none()
        return RequirementFileMapper.to_domain(model) if model else None

    @override
    async def save(self, entity: RequirementFile) -> RequirementFile:
        return await self._crud.save(entity)

    @override
    async def delete(self, entity_id: EntityID) -> bool:
        return await self._crud.delete(entity_id)
