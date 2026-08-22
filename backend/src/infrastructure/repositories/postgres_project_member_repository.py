"""PostgreSQL repository cho ProjectMember."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.project.entities import ProjectMember
from src.domain.project.i_project_member_repository import IProjectMemberRepository
from src.domain.shared.types import EntityID
from src.infrastructure.database.error_translation import translate_database_errors
from src.infrastructure.database.mappers.project_member_mapper import ProjectMemberMapper
from src.infrastructure.database.models.project_member import ProjectMemberModel
from src.infrastructure.repositories.sqlalchemy_crud import SqlAlchemyCrud
from typing_extensions import override


class PostgresProjectMemberRepository(IProjectMemberRepository):
    """Lưu trữ ProjectMember bằng SQLAlchemy AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._crud = SqlAlchemyCrud(session, ProjectMemberModel, ProjectMemberMapper)

    @override
    async def get_by_id(self, entity_id: EntityID) -> ProjectMember | None:
        """Lấy membership theo ID."""
        return await self._crud.get_by_id(entity_id)

    @override
    @translate_database_errors
    async def list_by_project(self, project_id: EntityID) -> list[ProjectMember]:
        """Lấy danh sách membership của Project."""
        statement = select(ProjectMemberModel).where(ProjectMemberModel.project_id == project_id)
        result = await self._session.execute(statement)
        return [ProjectMemberMapper.to_domain(model) for model in result.scalars().all()]

    @override
    @translate_database_errors
    async def get_by_project_and_user(
        self,
        project_id: EntityID,
        user_id: EntityID,
    ) -> ProjectMember | None:
        """Lấy membership theo khóa nghiệp vụ Project/User."""
        statement = select(ProjectMemberModel).where(
            ProjectMemberModel.project_id == project_id,
            ProjectMemberModel.user_id == user_id,
        )
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return ProjectMemberMapper.to_domain(model) if model else None

    @override
    async def save(self, entity: ProjectMember) -> ProjectMember:
        """Lưu mới hoặc cập nhật membership."""
        return await self._crud.save(entity)

    @override
    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa membership theo ID."""
        return await self._crud.delete(entity_id)
