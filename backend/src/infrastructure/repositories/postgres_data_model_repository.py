"""Triển khai PostgreSQL Repository cho thực thể DataModel."""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.data_model.entities import DataModel
from src.domain.data_model.repository import IDataModelRepository
from src.domain.shared.types import EntityID
from src.infrastructure.database.mappers.data_model_mapper import DataModelMapper
from src.infrastructure.database.models.data_model import DataModelModel
from typing_extensions import override


class PostgresDataModelRepository(IDataModelRepository):
    """Triển khai IDataModelRepository sử dụng AsyncSession và DataModelMapper."""

    def __init__(self, session: AsyncSession) -> None:
        """Khởi tạo repository với SQLAlchemy AsyncSession."""
        self._session: AsyncSession = session

    @override
    async def get_by_id(self, entity_id: EntityID) -> DataModel | None:
        """Lấy Mô hình dữ liệu theo ID."""
        stmt = select(DataModelModel).where(DataModelModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DataModelMapper.to_domain(model) if model else None

    @override
    async def get_by_project_id(self, project_id: EntityID) -> DataModel | None:
        """Lấy mô hình dữ liệu theo dự án."""
        stmt = select(DataModelModel).where(DataModelModel.project_id == project_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DataModelMapper.to_domain(model) if model else None

    @override
    async def save(self, entity: DataModel) -> DataModel:
        """Lưu (tạo mới hoặc cập nhật) thực thể DataModel."""
        stmt = select(DataModelModel).where(DataModelModel.id == entity.id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        if existing_model:
            model = DataModelMapper.update_model(existing_model, entity)
        else:
            model = DataModelMapper.to_model(entity)
            self._session.add(model)

        await self._session.flush()
        return DataModelMapper.to_domain(model)

    @override
    async def update_if_revision_matches(self, entity: DataModel, base_revision: int) -> DataModel | None:
        """Cập nhật DBML bằng optimistic locking."""
        stmt = (
            update(DataModelModel)
            .where(
                DataModelModel.id == entity.id,
                DataModelModel.revision == base_revision,
            )
            .values(
                dbml=entity.dbml,
                revision=entity.revision,
                updated_at=entity.updated_at,
            )
            .returning(DataModelModel)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DataModelMapper.to_domain(model) if model else None

    @override
    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa thực thể DataModel theo ID."""
        stmt = select(DataModelModel).where(DataModelModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True
