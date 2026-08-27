from datetime import datetime

from sqlalchemy import func, or_, select, union_all
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.utils.datetime import ensure_utc
from src.domain.project.entities import Project
from src.domain.project.i_project_repository import IProjectRepository
from src.domain.shared.types import EntityID
from src.infrastructure.database.error_translation import translate_database_errors
from src.infrastructure.database.mappers.project_mapper import ProjectMapper
from src.infrastructure.database.models.data_model import DataModelModel
from src.infrastructure.database.models.data_source import DataSourceModel
from src.infrastructure.database.models.project import ProjectModel
from src.infrastructure.database.models.project_member import ProjectMemberModel
from src.infrastructure.database.models.project_session import ProjectSessionModel
from src.infrastructure.database.models.requirement import RequirementModel
from src.infrastructure.database.models.requirement_file import RequirementFileModel
from src.infrastructure.database.models.sandbox_config import SandboxConfigModel
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
    async def get_by_id_for_update(self, entity_id: EntityID) -> Project | None:
        """Lấy Project bằng row lock để serialize revision mutation."""
        result = await self._session.execute(
            select(ProjectModel)
            .where(ProjectModel.id == entity_id)
            .with_for_update()
        )
        model = result.scalar_one_or_none()
        return ProjectMapper.to_domain(model) if model else None

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
    @translate_database_errors
    async def get_latest_activity_by_project_ids(
        self, project_ids: tuple[EntityID, ...]
    ) -> dict[EntityID, datetime]:
        """Tổng hợp mốc thời gian hoạt động mới nhất qua tất cả các module con."""
        if not project_ids:
            return {}
        queries = [
            select(ProjectModel.id.label("p_id"), ProjectModel.updated_at.label("u_at")).where(ProjectModel.id.in_(project_ids)),
            select(DataSourceModel.project_id.label("p_id"), DataSourceModel.updated_at.label("u_at")).where(DataSourceModel.project_id.in_(project_ids)),
            select(RequirementModel.project_id.label("p_id"), RequirementModel.updated_at.label("u_at")).where(RequirementModel.project_id.in_(project_ids)),
            select(RequirementFileModel.project_id.label("p_id"), RequirementFileModel.updated_at.label("u_at")).where(RequirementFileModel.project_id.in_(project_ids)),
            select(DataModelModel.project_id.label("p_id"), DataModelModel.updated_at.label("u_at")).where(DataModelModel.project_id.in_(project_ids)),
            select(ProjectSessionModel.project_id.label("p_id"), ProjectSessionModel.updated_at.label("u_at")).where(ProjectSessionModel.project_id.in_(project_ids)),
            select(SandboxConfigModel.project_id.label("p_id"), SandboxConfigModel.updated_at.label("u_at")).where(SandboxConfigModel.project_id.in_(project_ids)),
        ]
        union_subquery = union_all(*queries).subquery("activities")
        stmt = (
            select(union_subquery.c.p_id, func.max(union_subquery.c.u_at))
            .group_by(union_subquery.c.p_id)
        )
        result = await self._session.execute(stmt)
        return {row[0]: ensure_utc(row[1]) for row in result.all()}

    @override
    async def save(self, entity: Project) -> Project:
        """Lưu mới hoặc cập nhật Project."""
        return await self._crud.save(entity)

    @override
    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa Project theo ID."""
        return await self._crud.delete(entity_id)
