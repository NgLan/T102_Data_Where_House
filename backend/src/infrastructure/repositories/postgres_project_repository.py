"""Triển khai PostgreSQL Repository cho thực thể Project."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.project.entities import Project
from src.domain.project.repository import IProjectRepository
from src.domain.shared.types import EntityID
from src.infrastructure.database.mappers.project_mapper import ProjectMapper
from src.infrastructure.database.models.project import ProjectModel


class PostgresProjectRepository(IProjectRepository):
    """Triển khai IProjectRepository sử dụng SQLAlchemy AsyncSession và ProjectMapper."""

    def __init__(self, session: AsyncSession) -> None:
        """Khởi tạo repository với SQLAlchemy AsyncSession."""
        self._session: AsyncSession = session

    async def get_by_id(self, id: EntityID) -> Project | None:
        """Lấy dự án theo ID."""
        stmt = select(ProjectModel).where(ProjectModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return ProjectMapper.to_domain(model) if model else None

    async def list_by_user(self, user_id: EntityID) -> list[Project]:
        """Lấy danh sách dự án sở hữu bởi người dùng."""
        stmt = select(ProjectModel).where(ProjectModel.user_id == user_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [ProjectMapper.to_domain(m) for m in models]

    async def save(self, entity: Project) -> Project:
        """Lưu (tạo mới hoặc cập nhật) thực thể Project."""
        stmt = select(ProjectModel).where(ProjectModel.id == entity.id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        if existing_model:
            model = ProjectMapper.update_model(existing_model, entity)
        else:
            model = ProjectMapper.to_model(entity)
            self._session.add(model)

        await self._session.flush()
        return ProjectMapper.to_domain(model)

    async def delete(self, id: EntityID) -> None:
        """Xóa thực thể Project theo ID."""
        stmt = select(ProjectModel).where(ProjectModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
