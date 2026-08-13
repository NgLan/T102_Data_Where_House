"""Triển khai PostgreSQL Repository cho thực thể SessionEvent."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.project_session.entities import SessionEvent
from src.domain.project_session.repository import ISessionEventRepository
from src.domain.shared.types import EntityID
from src.infrastructure.database.mappers.session_event_mapper import SessionEventMapper
from src.infrastructure.database.models.session_event import SessionEventModel


class PostgresSessionEventRepository(ISessionEventRepository):
    """Triển khai ISessionEventRepository sử dụng AsyncSession và SessionEventMapper."""

    def __init__(self, session: AsyncSession) -> None:
        """Khởi tạo repository với SQLAlchemy AsyncSession."""
        self._session: AsyncSession = session

    async def get_by_id(self, id: EntityID) -> SessionEvent | None:
        """Lấy Sự kiện theo ID."""
        stmt = select(SessionEventModel).where(SessionEventModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return SessionEventMapper.to_domain(model) if model else None

    async def list_by_session(self, session_id: EntityID) -> list[SessionEvent]:
        """Danh sách các sự kiện thuộc một phiên làm việc."""
        stmt = (
            select(SessionEventModel)
            .where(SessionEventModel.session_id == session_id)
            .order_by(SessionEventModel.created_at.asc())
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [SessionEventMapper.to_domain(m) for m in models]

    async def save(self, entity: SessionEvent) -> SessionEvent:
        """Lưu (tạo mới hoặc cập nhật) thực thể SessionEvent."""
        stmt = select(SessionEventModel).where(SessionEventModel.id == entity.id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        if existing_model:
            model = SessionEventMapper.update_model(existing_model, entity)
        else:
            model = SessionEventMapper.to_model(entity)
            self._session.add(model)

        await self._session.flush()
        return SessionEventMapper.to_domain(model)

    async def delete(self, id: EntityID) -> None:
        """Xóa thực thể SessionEvent theo ID."""
        stmt = select(SessionEventModel).where(SessionEventModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
