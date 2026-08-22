"""PostgreSQL repository cho thực thể AnalyticalRequirement."""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.analytical_requirement.i_analytical_requirement_repository import (
    IAnalyticalRequirementRepository,
)
from src.domain.shared.types import EntityID
from src.infrastructure.database.error_translation import translate_database_errors
from src.infrastructure.database.mappers.analytical_requirement_mapper import (
    AnalyticalRequirementMapper,
)
from src.infrastructure.database.models.analytical_requirement import AnalyticalRequirementModel
from src.infrastructure.database.models.requirement import RequirementModel
from src.infrastructure.repositories.sqlalchemy_crud import SqlAlchemyCrud
from typing_extensions import override


class PostgresAnalyticalRequirementRepository(IAnalyticalRequirementRepository):
    """Lưu trữ AnalyticalRequirement bằng SQLAlchemy AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._crud = SqlAlchemyCrud(session, AnalyticalRequirementModel, AnalyticalRequirementMapper)

    @override
    async def get_by_id(self, entity_id: EntityID) -> AnalyticalRequirement | None:
        """Lấy yêu cầu phân tích theo ID."""
        return await self._crud.get_by_id(entity_id)

    @override
    @translate_database_errors
    async def get_by_requirement_id(self, requirement_id: EntityID) -> list[AnalyticalRequirement]:
        """Lấy các yêu cầu phân tích theo yêu cầu gốc."""
        statement = select(AnalyticalRequirementModel).where(
            AnalyticalRequirementModel.requirement_id == requirement_id
        )
        result = await self._session.execute(statement)
        return [AnalyticalRequirementMapper.to_domain(model) for model in result.scalars().all()]

    @override
    @translate_database_errors
    async def list_by_project(
        self, project_id: EntityID
    ) -> list[AnalyticalRequirement]:
        """Lấy AnalyticalRequirements qua quan hệ Requirement của dự án."""
        statement = select(AnalyticalRequirementModel).join(RequirementModel).where(
            RequirementModel.project_id == project_id
        )
        result = await self._session.execute(statement)
        return [AnalyticalRequirementMapper.to_domain(model) for model in result.scalars()]

    @override
    @translate_database_errors
    async def replace_by_project(
        self,
        project_id: EntityID,
        entities: tuple[AnalyticalRequirement, ...],
    ) -> list[AnalyticalRequirement]:
        """Thay tập phân tích cũ trong cùng transaction."""
        requirement_ids = select(RequirementModel.id).where(
            RequirementModel.project_id == project_id
        )
        await self._session.execute(
            delete(AnalyticalRequirementModel).where(
                AnalyticalRequirementModel.requirement_id.in_(requirement_ids)
            )
        )
        models = [AnalyticalRequirementMapper.to_model(entity) for entity in entities]
        self._session.add_all(models)
        await self._session.flush()
        return [AnalyticalRequirementMapper.to_domain(model) for model in models]

    @override
    async def save(self, entity: AnalyticalRequirement) -> AnalyticalRequirement:
        """Lưu mới hoặc cập nhật yêu cầu phân tích."""
        return await self._crud.save(entity)

    @override
    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa yêu cầu phân tích theo ID."""
        return await self._crud.delete(entity_id)
