"""Application service duy nhất cho module Data Model."""

from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_models.i_data_model_service import IDataModelService
from src.application.data_models.input import (
    GenerateDataModelInput,
    GetDataModelInput,
    UpdateDataModelInput,
)
from src.application.data_models.output import DataModelOutput
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.logging import get_logger
from src.domain.analytical_requirement.repository import IAnalyticalRequirementRepository
from src.domain.data_model.entities import DataModel
from src.domain.data_model.generation import IDataModelGenerator
from src.domain.data_model.repository import IDataModelRepository
from src.domain.data_source.repository import IDataSourceRepository
from src.domain.requirement.repository import IRequirementRepository
from typing_extensions import override

logger = get_logger(__name__)


class DataModelService(IDataModelService):
    """Điều phối các use case của Data Model qua domain repository."""

    def __init__(
        self,
        repository: IDataModelRepository,
        unit_of_work: IUnitOfWork,
        requirement_repository: IRequirementRepository | None = None,
        data_source_repository: IDataSourceRepository | None = None,
        analytical_repository: IAnalyticalRequirementRepository | None = None,
        generator: IDataModelGenerator | None = None,
    ) -> None:
        """Khởi tạo service với repository và transaction abstraction.

        Bốn tham số cuối chỉ cần cho use case sinh mô hình bằng AI (T-019); các use case
        đọc/ghi thủ công vẫn hoạt động khi chúng để trống.
        """
        self._repository = repository
        self._unit_of_work = unit_of_work
        self._requirement_repository = requirement_repository
        self._data_source_repository = data_source_repository
        self._analytical_repository = analytical_repository
        self._generator = generator

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

    @override
    async def generate_data_model(self, data: GenerateDataModelInput) -> DataModelOutput:
        """Chạy pipeline AI sinh Data Model từ yêu cầu và nguồn dữ liệu của dự án."""
        self._ensure_generation_ready()

        requirements = await self._requirement_repository.list_by_project(data.project_id)
        data_sources = await self._data_source_repository.list_by_project(data.project_id)
        if not requirements and not data_sources:
            raise BusinessException(
                code=ErrorCode.INVALID_DATA_MODEL,
                message=(
                    "Dự án chưa có yêu cầu nghiệp vụ hoặc nguồn dữ liệu nào "
                    "để AI phân tích."
                ),
            )

        result = await self._generator.generate(requirements, data_sources)

        await self._persist_analysis(data_sources, result)
        saved = await self._persist_data_model(data.project_id, result.dbml)
        await self._unit_of_work.commit()

        logger.info(
            "data_model_generated project_id=%s revision=%d attempts=%d",
            data.project_id,
            saved.revision,
            result.attempts,
        )
        return DataModelOutput.from_domain(saved)

    def _ensure_generation_ready(self) -> None:
        """Chặn sớm khi service được dựng thiếu phụ thuộc dành cho pipeline AI."""
        missing = (
            self._requirement_repository is None
            or self._data_source_repository is None
            or self._analytical_repository is None
            or self._generator is None
        )
        if missing:
            raise BusinessException(
                code=ErrorCode.INTERNAL_SERVER_ERROR,
                message="Chức năng sinh mô hình bằng AI chưa được cấu hình đầy đủ.",
            )

    async def _persist_analysis(self, data_sources, result) -> None:  # noqa: ANN001
        """Lưu schema đã phân tích và các yêu cầu phân tích do agent sinh ra."""
        for data_source in data_sources:
            data_source.schema_metadata = result.analyzed_schema
            await self._data_source_repository.save(data_source)

        for analytical in result.analytical_requirements:
            await self._analytical_repository.save(analytical)

    async def _persist_data_model(self, project_id, dbml: str) -> DataModel:  # noqa: ANN001
        """Tạo mới Data Model hoặc cập nhật bản hiện có bằng optimistic locking."""
        current = await self._repository.get_by_project_id(project_id)
        if current is None:
            return await self._repository.save(DataModel(project_id=project_id, dbml=dbml))

        base_revision = current.revision
        current.update_dbml(dbml, base_revision)
        updated = await self._repository.update_if_revision_matches(current, base_revision)
        if updated is None:
            raise BusinessException(
                code=ErrorCode.REVISION_CONFLICT,
                message="Data Model đã được cập nhật bởi một thao tác khác.",
            )
        return updated

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
