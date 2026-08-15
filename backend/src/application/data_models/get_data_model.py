"""Use Case: Lấy mô hình dữ liệu hiện hành của một dự án."""

from src.application.data_models.dto import DataModelOutput, GetDataModelInput
from src.application.data_models.i_get_data_model_service import IGetDataModelService
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_model.entities import DataModel
from src.domain.data_model.repository import IDataModelRepository


class GetDataModelService(IGetDataModelService):
    """Triển khai use case truy vấn mô hình dữ liệu theo dự án."""

    def __init__(self, data_model_repository: IDataModelRepository) -> None:
        """Khởi tạo use case với repository mô hình dữ liệu."""
        self._data_model_repository: IDataModelRepository = data_model_repository

    async def execute(self, payload: GetDataModelInput) -> DataModelOutput:
        """Trả về mô hình dữ liệu hiện hành của dự án."""
        data_model: DataModel | None = await self._data_model_repository.get_by_project_id(
            payload.project_id
        )
        if data_model is None:
            raise BusinessException(
                code=ErrorCode.DATA_MODEL_NOT_FOUND,
                message=f"Dự án '{payload.project_id}' chưa có mô hình dữ liệu nào.",
            )

        return DataModelOutput(
            id=data_model.id,
            project_id=data_model.project_id,
            dbml=data_model.dbml,
            revision=data_model.revision,
            created_at=data_model.created_at,
            updated_at=data_model.updated_at,
        )
