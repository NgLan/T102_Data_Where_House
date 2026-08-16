"""Hiện thực hóa Use Case Lấy Mô hình Dữ liệu của Dự án."""

from uuid import UUID

from src.application.data_models.dto import DataModelDto
from src.application.data_models.IGetDataModelService import IGetDataModelService
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.utils.datetime import to_isoformat
from src.domain.data_model.entities import DataModel
from src.domain.data_model.repository import IDataModelRepository
from src.domain.project.repository import IProjectRepository


class GetDataModelService(IGetDataModelService):
    """Xử lý truy vấn thông tin mô hình dữ liệu của một dự án."""

    def __init__(
        self,
        data_model_repo: IDataModelRepository,
        project_repo: IProjectRepository,
    ) -> None:
        """Khởi tạo use case service với các repository cần thiết."""
        self._data_model_repo = data_model_repo
        self._project_repo = project_repo

    async def execute(self, project_id: UUID) -> DataModelDto | None:
        """Thực thi truy vấn thông tin DataModel theo ID dự án."""
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise BusinessException(
                code=ErrorCode.PROJECT_NOT_FOUND,
                message="Dự án không tồn tại.",
            )

        data_model = await self._data_model_repo.get_by_project_id(project_id)
        if not data_model:
            return None

        return self._map_to_dto(data_model)

    def _map_to_dto(self, data_model: DataModel) -> DataModelDto:
        """Chuyển đổi thực thể DataModel sang DataModelDto."""
        return DataModelDto(
            id=data_model.id,
            project_id=data_model.project_id,
            dbml=data_model.dbml,
            revision=data_model.revision,
            created_at=to_isoformat(data_model.created_at),
            updated_at=to_isoformat(data_model.updated_at),
        )
