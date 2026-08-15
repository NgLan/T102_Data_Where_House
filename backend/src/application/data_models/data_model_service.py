"""Application service duy nhất cho module Data Model."""

from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_models.i_data_model_service import IDataModelService
from src.application.data_models.input import GetDataModelInput, UpdateDataModelInput
from src.application.data_models.output import DataModelOutput
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_model.entities import DataModel
from src.domain.data_model.repository import IDataModelRepository
from typing_extensions import override


class DataModelService(IDataModelService):
    """Điều phối các use case của Data Model qua domain repository."""

    def __init__(self, repository: IDataModelRepository, unit_of_work: IUnitOfWork) -> None:
        """Khởi tạo service với repository và transaction abstraction."""
        self._repository = repository
        self._unit_of_work = unit_of_work

    @override
    async def get_data_model(self, data: GetDataModelInput) -> DataModelOutput:
        """Lấy Data Model theo project và chuẩn hóa lỗi không tồn tại."""
        data_model = await self._repository.get_by_project_id(data.project_id)
        if data_model is None:
            raise BusinessException(
                code=ErrorCode.DATA_MODEL_NOT_FOUND,
                message="Không tìm thấy Data Model của dự án.",
            )
        return DataModelOutput.from_domain(data_model)

    @override
    async def update_data_model(self, data: UpdateDataModelInput) -> DataModelOutput:
        """Cập nhật DBML dựa trên base revision."""
        current = self._get_target(await self._repository.get_by_project_id(data.project_id), data)
        current.update_dbml(data.dbml, data.base_revision)
        updated = await self._repository.update_if_revision_matches(current, data.base_revision)
        if updated is None:
            raise BusinessException(
                code=ErrorCode.REVISION_CONFLICT,
                message="Data Model đã được cập nhật bởi một thao tác khác.",
            )
        await self._unit_of_work.commit()
        return DataModelOutput.from_domain(updated)

    @staticmethod
    def _get_target(current: DataModel | None, data: UpdateDataModelInput) -> DataModel:
        """Kiểm tra và trả Data Model đúng ID trong input."""
        if current is None:
            raise BusinessException(
                code=ErrorCode.DATA_MODEL_NOT_FOUND,
                message="Không tìm thấy Data Model của dự án.",
            )
        if current.id != data.data_model_id:
            raise BusinessException(
                code=ErrorCode.INVALID_DATA_MODEL,
                message="Data Model không thuộc dự án được yêu cầu.",
            )
        return current
