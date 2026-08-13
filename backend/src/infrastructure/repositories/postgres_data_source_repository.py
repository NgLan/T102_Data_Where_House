"""Triển khai PostgreSQL Repository cho thực thể DataSource."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.data_source.entities import DataSource
from src.domain.data_source.repository import IDataSourceRepository
from src.domain.shared.types import EntityID
from src.infrastructure.database.mappers.data_source_mapper import DataSourceMapper
from src.infrastructure.database.models.data_source import DataSourceModel


class PostgresDataSourceRepository(IDataSourceRepository):
    """Triển khai IDataSourceRepository sử dụng AsyncSession và DataSourceMapper."""

    def __init__(self, session: AsyncSession) -> None:
        """Khởi tạo repository với SQLAlchemy AsyncSession."""
        self._session: AsyncSession = session

    async def get_by_id(self, id: EntityID) -> DataSource | None:
        """Lấy Nguồn dữ liệu theo ID."""
        stmt = select(DataSourceModel).where(DataSourceModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DataSourceMapper.to_domain(model) if model else None

    async def list_by_project(self, project_id: EntityID) -> list[DataSource]:
        """Lấy danh sách nguồn dữ liệu thuộc một dự án."""
        stmt = select(DataSourceModel).where(DataSourceModel.project_id == project_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [DataSourceMapper.to_domain(m) for m in models]

    async def save(self, entity: DataSource) -> DataSource:
        """Lưu (tạo mới hoặc cập nhật) thực thể DataSource."""
        stmt = select(DataSourceModel).where(DataSourceModel.id == entity.id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        if existing_model:
            model = DataSourceMapper.update_model(existing_model, entity)
        else:
            model = DataSourceMapper.to_model(entity)
            self._session.add(model)

        await self._session.flush()
        return DataSourceMapper.to_domain(model)

    async def delete(self, id: EntityID) -> None:
        """Xóa thực thể DataSource theo ID."""
        stmt = select(DataSourceModel).where(DataSourceModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
