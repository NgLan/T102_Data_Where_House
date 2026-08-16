"""Hiện thực hóa Use Case Cập nhật Mã DBML Mô hình Dữ liệu (UC5.1.1)."""

from src.application.data_models.dto import DataModelDto, UpdateDataModelCommand
from src.application.data_models.IUpdateDataModelService import IUpdateDataModelService
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.utils.datetime import to_isoformat
from src.domain.data_model.entities import DataModel
from src.domain.data_model.repository import IDataModelRepository
from src.domain.project.repository import IProjectRepository


class UpdateDataModelService(IUpdateDataModelService):
    """Xử lý cập nhật mã DBML thủ công và đồng bộ phiên bản revision."""

    def __init__(
        self,
        data_model_repo: IDataModelRepository,
        project_repo: IProjectRepository,
    ) -> None:
        """Khởi tạo use case service với các repository cần thiết."""
        self._data_model_repo = data_model_repo
        self._project_repo = project_repo

    async def execute(self, command: UpdateDataModelCommand) -> DataModelDto:
        """Thực thi cập nhật mã DBML vào cơ sở dữ liệu PostgreSQL."""
        await self._ensure_project_exists(command.project_id)

        data_model = await self._data_model_repo.get_by_project_id(command.project_id)
        if data_model:
            data_model.update_dbml(command.dbml, command.expected_revision)
        else:
            data_model = DataModel(
                project_id=command.project_id,
                dbml=command.dbml,
                revision=1,
            )

        saved_data_model = await self._data_model_repo.save(data_model)
        return self._map_to_dto(saved_data_model)

    async def _ensure_project_exists(self, project_id: object) -> None:
        """Kiểm tra dự án có tồn tại trong hệ thống trước khi lưu data model."""
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise BusinessException(
                code=ErrorCode.PROJECT_NOT_FOUND,
                message="Dự án không tồn tại.",
            )

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
