"""PostgreSQL repository cho DataSource."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.data_source.entities import DataSource
from src.domain.data_source.i_data_source_repository import IDataSourceRepository
from src.domain.shared.types import EntityID
from src.infrastructure.database.error_translation import translate_database_errors
from src.infrastructure.database.mappers.data_source_mapper import DataSourceMapper
from src.infrastructure.database.models.data_source import DataSourceModel
from src.infrastructure.repositories.sqlalchemy_crud import SqlAlchemyCrud
from typing_extensions import override


class PostgresDataSourceRepository(IDataSourceRepository):
    """Lưu trữ DataSource bằng SQLAlchemy AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._crud = SqlAlchemyCrud(session, DataSourceModel, DataSourceMapper)

    @override
    async def get_by_id(self, entity_id: EntityID) -> DataSource | None:
        """Lấy DataSource theo ID."""
        return await self._crud.get_by_id(entity_id)

    @override
    @translate_database_errors
    async def list_by_project(self, project_id: EntityID) -> list[DataSource]:
        """Lấy DataSource thuộc một Project."""
        result = await self._session.execute(
            select(DataSourceModel).where(DataSourceModel.project_id == project_id)
        )
        return [DataSourceMapper.to_domain(model) for model in result.scalars().all()]

    @override
    @translate_database_errors
    async def count_by_project_ids(self, project_ids: tuple[EntityID, ...]) -> dict[EntityID, int]:
        """Đếm DataSource theo Project bằng một aggregate query."""
        if not project_ids:
            return {}
        statement = (
            select(DataSourceModel.project_id, func.count(DataSourceModel.id))
            .where(DataSourceModel.project_id.in_(project_ids))
            .group_by(DataSourceModel.project_id)
        )
        result = await self._session.execute(statement)
        return {project_id: count for project_id, count in result.all()}

    @override
    async def save(self, entity: DataSource) -> DataSource:
        """Lưu mới hoặc cập nhật DataSource."""
        return await self._crud.save(entity)

    @override
    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa DataSource theo ID."""
        return await self._crud.delete(entity_id)
