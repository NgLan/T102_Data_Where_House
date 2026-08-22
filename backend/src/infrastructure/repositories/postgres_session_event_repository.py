"""PostgreSQL repository cho thực thể SessionEvent."""

from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.project_session.entities import SessionEvent
from src.domain.project_session.i_session_event_repository import ISessionEventRepository
from src.domain.shared.types import EntityID
from src.infrastructure.database.error_translation import translate_database_errors
from src.infrastructure.database.mappers.session_event.session_event_mapper import SessionEventMapper
from src.infrastructure.database.models.session_event import SessionEventModel
from src.infrastructure.repositories.sqlalchemy_crud import SqlAlchemyCrud
from typing_extensions import override


class PostgresSessionEventRepository(ISessionEventRepository):
    """Lưu trữ SessionEvent bằng SQLAlchemy AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._crud = SqlAlchemyCrud(session, SessionEventModel, SessionEventMapper)

    @override
    async def get_by_id(self, entity_id: EntityID) -> SessionEvent | None:
        """Lấy sự kiện phiên theo ID."""
        return await self._crud.get_by_id(entity_id)

    @override
    @translate_database_errors
    async def list_by_session(
        self,
        session_id: EntityID,
        after_id: EntityID | None = None,
        limit: int = 50,
    ) -> list[SessionEvent]:
        """Lấy các sự kiện theo thứ tự phát sinh."""
        statement = select(SessionEventModel).where(SessionEventModel.session_id == session_id)
        if after_id is not None:
            cursor = await self._crud.get_by_id(after_id)
            if cursor is None or cursor.session_id != session_id:
                return []
            statement = statement.where(
                tuple_(SessionEventModel.created_at, SessionEventModel.id)
                > tuple_(cursor.created_at, cursor.id)
            )
        statement = statement.order_by(
            SessionEventModel.created_at.asc(), SessionEventModel.id.asc()
        ).limit(limit)
        result = await self._session.execute(statement)
        return [SessionEventMapper.to_domain(model) for model in result.scalars().all()]

    @override
    async def save(self, entity: SessionEvent) -> SessionEvent:
        """Lưu mới hoặc cập nhật sự kiện phiên."""
        return await self._crud.save(entity)

    @override
    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa sự kiện phiên theo ID."""
        return await self._crud.delete(entity_id)
