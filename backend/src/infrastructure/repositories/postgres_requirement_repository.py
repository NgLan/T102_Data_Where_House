"""PostgreSQL repository cho thực thể Requirement."""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.requirement.entities import Requirement
from src.domain.requirement.i_requirement_repository import IRequirementRepository
from src.domain.shared.types import EntityID
from src.infrastructure.database.error_translation import translate_database_errors
from src.infrastructure.database.mappers.requirement_mapper import RequirementMapper
from src.infrastructure.database.models.requirement import RequirementModel
from src.infrastructure.repositories.sqlalchemy_crud import SqlAlchemyCrud
from typing_extensions import override


class PostgresRequirementRepository(IRequirementRepository):
    """Lưu trữ Requirement bằng SQLAlchemy AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._crud = SqlAlchemyCrud(session, RequirementModel, RequirementMapper)

    @override
    async def get_by_id(self, entity_id: EntityID) -> Requirement | None:
        """Lấy yêu cầu theo ID."""
        return await self._crud.get_by_id(entity_id)

    @override
    @translate_database_errors
    async def list_by_project(self, project_id: EntityID) -> list[Requirement]:
        """Lấy các yêu cầu thuộc dự án."""
        statement = select(RequirementModel).where(RequirementModel.project_id == project_id)
        result = await self._session.execute(statement)
        return [RequirementMapper.to_domain(model) for model in result.scalars().all()]

    @override
    @translate_database_errors
    async def replace_by_project(
        self, project_id: EntityID, entities: tuple[Requirement, ...]
    ) -> list[Requirement]:
        """Xóa tập cũ và flush tập Requirements mới trong cùng transaction."""
        await self._session.execute(
            delete(RequirementModel).where(RequirementModel.project_id == project_id)
        )
        models = [RequirementMapper.to_model(entity) for entity in entities]
        self._session.add_all(models)
        await self._session.flush()
        return [RequirementMapper.to_domain(model) for model in models]

    @override
    async def save(self, entity: Requirement) -> Requirement:
        """Lưu mới hoặc cập nhật yêu cầu."""
        return await self._crud.save(entity)

    @override
    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa yêu cầu theo ID."""
        return await self._crud.delete(entity_id)
