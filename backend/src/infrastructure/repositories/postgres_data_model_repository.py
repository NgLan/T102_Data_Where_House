"""Triển khai PostgreSQL Repository cho thực thể DataModel."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.data_model.entities import DataModel
from src.domain.data_model.repository import IDataModelRepository
from src.domain.shared.types import EntityID
from src.infrastructure.database.mappers.data_model_mapper import DataModelMapper
from src.infrastructure.database.models.data_model import DataModelModel


class PostgresDataModelRepository(IDataModelRepository):
    """Triển khai IDataModelRepository sử dụng AsyncSession và DataModelMapper."""

    def __init__(self, session: AsyncSession) -> None:
        """Khởi tạo repository với SQLAlchemy AsyncSession."""
        self._session: AsyncSession = session

    async def get_by_id(self, id: EntityID) -> DataModel | None:
        """Lấy Mô hình dữ liệu theo ID."""
        stmt = select(DataModelModel).where(DataModelModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DataModelMapper.to_domain(model) if model else None

    async def get_by_project_id(self, project_id: EntityID) -> DataModel | None:
        """Lấy mô hình dữ liệu theo dự án."""
        stmt = select(DataModelModel).where(DataModelModel.project_id == project_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DataModelMapper.to_domain(model) if model else None

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

    async def delete(self, id: EntityID) -> None:
        """Xóa thực thể DataModel theo ID."""
        stmt = select(DataModelModel).where(DataModelModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
