"""PostgreSQL repository cho Project aggregate."""

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.project.entities import Project
from src.domain.project.i_project_repository import IProjectRepository
from src.domain.shared.types import EntityID
from src.infrastructure.database.error_translation import translate_database_errors
from src.infrastructure.database.mappers.project_mapper import ProjectMapper
from src.infrastructure.database.models.project import ProjectModel
from src.infrastructure.database.models.project_member import ProjectMemberModel
from src.infrastructure.repositories.sqlalchemy_crud import SqlAlchemyCrud
from typing_extensions import override


class PostgresProjectRepository(IProjectRepository):
    """Lưu trữ Project bằng SQLAlchemy AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._crud = SqlAlchemyCrud(session, ProjectModel, ProjectMapper)

    @override
    async def get_by_id(self, entity_id: EntityID) -> Project | None:
        """Lấy Project theo ID."""
        return await self._crud.get_by_id(entity_id)

    @override
    @translate_database_errors
    async def list_accessible_by_user(self, user_id: EntityID) -> list[Project]:
        """Lấy Project actor sở hữu hoặc có membership, mới cập nhật trước."""
        statement = (
            select(ProjectModel)
            .outerjoin(ProjectMemberModel, ProjectMemberModel.project_id == ProjectModel.id)
            .where(or_(ProjectModel.user_id == user_id, ProjectMemberModel.user_id == user_id))
            .distinct()
            .order_by(ProjectModel.updated_at.desc())
        )
        result = await self._session.execute(statement)
        return [ProjectMapper.to_domain(model) for model in result.scalars().all()]

    @override
    async def save(self, entity: Project) -> Project:
        """Lưu mới hoặc cập nhật Project."""
        return await self._crud.save(entity)

    @override
    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa Project theo ID."""
        return await self._crud.delete(entity_id)
