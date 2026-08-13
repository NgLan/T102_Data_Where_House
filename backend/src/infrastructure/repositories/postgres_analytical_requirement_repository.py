"""Triển khai PostgreSQL Repository cho thực thể AnalyticalRequirement."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.analytical_requirement.repository import IAnalyticalRequirementRepository
from src.domain.shared.types import EntityID
from src.infrastructure.database.mappers.analytical_requirement_mapper import (
    AnalyticalRequirementMapper,
)
from src.infrastructure.database.models.analytical_requirement import (
    AnalyticalRequirementModel,
)


class PostgresAnalyticalRequirementRepository(IAnalyticalRequirementRepository):
    """Triển khai IAnalyticalRequirementRepository sử dụng AsyncSession và AnalyticalRequirementMapper."""

    def __init__(self, session: AsyncSession) -> None:
        """Khởi tạo repository với SQLAlchemy AsyncSession."""
        self._session: AsyncSession = session

    async def get_by_id(self, id: EntityID) -> AnalyticalRequirement | None:
        """Lấy Yêu cầu Phân tích theo ID."""
        stmt = select(AnalyticalRequirementModel).where(AnalyticalRequirementModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return AnalyticalRequirementMapper.to_domain(model) if model else None

    async def get_by_requirement_id(self, requirement_id: EntityID) -> list[AnalyticalRequirement]:
        """Lấy danh sách chi tiết phân tích theo ID yêu cầu gốc."""
        stmt = select(AnalyticalRequirementModel).where(
            AnalyticalRequirementModel.requirement_id == requirement_id
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [AnalyticalRequirementMapper.to_domain(m) for m in models]

    async def save(self, entity: AnalyticalRequirement) -> AnalyticalRequirement:
        """Lưu (tạo mới hoặc cập nhật) thực thể AnalyticalRequirement."""
        stmt = select(AnalyticalRequirementModel).where(AnalyticalRequirementModel.id == entity.id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        if existing_model:
            model = AnalyticalRequirementMapper.update_model(existing_model, entity)
        else:
            model = AnalyticalRequirementMapper.to_model(entity)
            self._session.add(model)

        await self._session.flush()
        return AnalyticalRequirementMapper.to_domain(model)

    async def delete(self, id: EntityID) -> None:
        """Xóa thực thể AnalyticalRequirement theo ID."""
        stmt = select(AnalyticalRequirementModel).where(AnalyticalRequirementModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
