"""Use Case: Sinh mã DDL từ mô hình dữ liệu DBML (UC5.4 / UC5.5)."""

from src.application.data_models.dto import GenerateDdlInput, GenerateDdlOutput
from src.application.data_models.i_generate_ddl_service import IGenerateDdlService
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_model.codegen import DdlGenerationResult, IDdlGenerator
from src.domain.data_model.entities import DataModel
from src.domain.data_model.repository import IDataModelRepository


class GenerateDdlService(IGenerateDdlService):
    """Triển khai use case biên dịch DBML của mô hình dữ liệu thành script DDL."""

    def __init__(
        self,
        data_model_repository: IDataModelRepository,
        ddl_generator: IDdlGenerator,
    ) -> None:
        """Khởi tạo use case với repository mô hình dữ liệu và bộ sinh mã DDL."""
        self._data_model_repository: IDataModelRepository = data_model_repository
        self._ddl_generator: IDdlGenerator = ddl_generator

    async def execute(self, payload: GenerateDdlInput) -> GenerateDdlOutput:
        """Trả về script DDL tương ứng với mô hình dữ liệu và dialect đã chọn."""
        data_model: DataModel | None = await self._data_model_repository.get_by_id(
            payload.data_model_id
        )
        if data_model is None:
            raise BusinessException(
                code=ErrorCode.DATA_MODEL_NOT_FOUND,
                message=f"Không tìm thấy mô hình dữ liệu '{payload.data_model_id}'.",
            )

        result: DdlGenerationResult = self._ddl_generator.generate(
            data_model.dbml,
            payload.dialect,
            payload.schema_name,
        )
        return GenerateDdlOutput(
            data_model_id=data_model.id,
            revision=data_model.revision,
            dialect=result.dialect,
            schema_name=result.schema_name,
            ddl=result.ddl,
            table_count=result.table_count,
            warnings=result.warnings,
        )
