"""PostgreSQL repository cho thực thể DataModel."""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.data_model.entities import DataModel
from src.domain.data_model.i_data_model_repository import IDataModelRepository
from src.domain.shared.types import EntityID
from src.infrastructure.database.error_translation import translate_database_errors
from src.infrastructure.database.mappers.data_source.data_model_mapper import DataModelMapper
from src.infrastructure.database.models.data_model import DataModelModel
from src.infrastructure.repositories.sqlalchemy_crud import SqlAlchemyCrud
from typing_extensions import override


class PostgresDataModelRepository(IDataModelRepository):
    """Lưu trữ DataModel bằng SQLAlchemy AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._crud = SqlAlchemyCrud(session, DataModelModel, DataModelMapper)

    @override
    async def get_by_id(self, entity_id: EntityID) -> DataModel | None:
        """Lấy Data Model theo ID."""
        return await self._crud.get_by_id(entity_id)

    @override
    @translate_database_errors
    async def get_by_project_id(self, project_id: EntityID) -> DataModel | None:
        """Lấy Data Model theo dự án."""
        result = await self._session.execute(
            select(DataModelModel).where(DataModelModel.project_id == project_id)
        )
        model = result.scalar_one_or_none()
        return DataModelMapper.to_domain(model) if model else None

    @override
    @translate_database_errors
    async def list_by_project_ids(
        self,
        project_ids: tuple[EntityID, ...],
    ) -> dict[EntityID, DataModel]:
        """Lấy Data Model theo nhiều Project bằng một query."""
        if not project_ids:
            return {}
        result = await self._session.execute(
            select(DataModelModel).where(DataModelModel.project_id.in_(project_ids))
        )
        models = (DataModelMapper.to_domain(model) for model in result.scalars().all())
        return {model.project_id: model for model in models}

    @override
    async def save(self, entity: DataModel) -> DataModel:
        """Lưu mới hoặc cập nhật Data Model."""
        return await self._crud.save(entity)

    @override
    @translate_database_errors
    async def update_if_revision_matches(
        self,
        entity: DataModel,
        base_revision: int,
    ) -> DataModel | None:
        """Cập nhật DBML bằng optimistic locking."""
        statement = (
            update(DataModelModel)
            .where(DataModelModel.id == entity.id, DataModelModel.revision == base_revision)
            .values(
                dbml=entity.dbml,
                revision=entity.revision,
                generated_from_requirement_revision=(
                    entity.generated_from_requirement_revision
                ),
                generated_from_source_revision=entity.generated_from_source_revision,
                updated_at=entity.updated_at,
            )
            .returning(DataModelModel)
        )
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return DataModelMapper.to_domain(model) if model else None

    @override
    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa Data Model theo ID."""
        return await self._crud.delete(entity_id)
