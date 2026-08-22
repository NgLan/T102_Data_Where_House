"""Triển khai PostgreSQL Repository cho thực thể DataModelChange."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_model.entities import DataModelChange
from src.domain.data_model.enums import DataModelChangeStatus
from src.domain.data_model.i_data_model_change_repository import IDataModelChangeRepository
from src.domain.shared.types import EntityID
from src.infrastructure.database.error_translation import translate_database_errors
from src.infrastructure.database.mappers.data_model_change_mapper import (
    DataModelChangeMapper,
)
from src.infrastructure.database.models.data_model_change import (
    ACTIVE_PROPOSAL_UNIQUE_INDEX,
    DataModelChangeModel,
)
from typing_extensions import override


class PostgresDataModelChangeRepository(IDataModelChangeRepository):
    """Triển khai IDataModelChangeRepository sử dụng AsyncSession và DataModelChangeMapper."""

    def __init__(self, session: AsyncSession) -> None:
        """Khởi tạo repository với SQLAlchemy AsyncSession."""
        self._session: AsyncSession = session

    @override
    @translate_database_errors
    async def get_by_id(self, entity_id: EntityID) -> DataModelChange | None:
        """Lấy Đề xuất Thay đổi theo ID."""
        stmt = select(DataModelChangeModel).where(DataModelChangeModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DataModelChangeMapper.to_domain(model) if model else None

    @override
    @translate_database_errors
    async def get_proposed_by_data_model_and_user(
        self,
        data_model_id: EntityID,
        user_id: EntityID,
    ) -> DataModelChange | None:
        """Lấy đề xuất PROPOSED duy nhất của người dùng trên Data Model."""
        stmt = select(DataModelChangeModel).where(
            DataModelChangeModel.data_model_id == data_model_id,
            DataModelChangeModel.user_id == user_id,
            DataModelChangeModel.status == DataModelChangeStatus.PROPOSED.value,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DataModelChangeMapper.to_domain(model) if model else None

    @override
    @translate_database_errors
    async def save(self, entity: DataModelChange) -> DataModelChange:
        """Lưu (tạo mới hoặc cập nhật) thực thể DataModelChange."""
        stmt = select(DataModelChangeModel).where(DataModelChangeModel.id == entity.id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        if existing_model:
            model = DataModelChangeMapper.update_model(existing_model, entity)
        else:
            model = DataModelChangeMapper.to_model(entity)
            self._session.add(model)

        try:
            await self._session.flush()
        except IntegrityError as exc:
            if ACTIVE_PROPOSAL_UNIQUE_INDEX in str(exc.orig):
                raise BusinessException(
                    code=ErrorCode.DATA_MODEL_CHANGE_ALREADY_PENDING,
                    message="Người dùng đã có một đề xuất đang chờ trên Data Model này.",
                ) from exc
            raise
        return DataModelChangeMapper.to_domain(model)

    @override
    @translate_database_errors
    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa thực thể DataModelChange theo ID."""
        stmt = select(DataModelChangeModel).where(DataModelChangeModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True
