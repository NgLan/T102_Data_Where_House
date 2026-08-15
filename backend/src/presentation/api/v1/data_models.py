"""API Endpoints v1 cho Mô hình Dữ liệu (Data Models) — UC5.4, UC5.5, UC6.1."""

from uuid import UUID

from fastapi import APIRouter, Query
from src.application.data_models.dto import (
    GenerateDdlInput,
    GetDataModelInput,
    ListChangeProposalsInput,
)
from src.common.dto.response import ApiResponse
from src.domain.data_model.enums import DataModelChangeStatus, SqlDialect
from src.presentation.dependencies.application import (
    GenerateDdlUseCase,
    GetDataModelUseCase,
    ListChangeProposalsUseCase,
)
from src.presentation.schemas.data_model_changes.response import (
    ChangeProposalSummaryResponse,
)
from src.presentation.schemas.data_models.response import (
    DataModelResponse,
    DdlGenerationResponse,
)

router = APIRouter(tags=["Data Models"])


@router.get(
    "/projects/{project_id}/data-model",
    response_model=ApiResponse[DataModelResponse],
    summary="Lấy mô hình dữ liệu hiện hành của một dự án",
)
async def get_project_data_model(
    project_id: UUID,
    use_case: GetDataModelUseCase,
) -> ApiResponse[DataModelResponse]:
    """Trả về nội dung DBML chính thức và revision hiện tại của dự án."""
    result = await use_case.execute(GetDataModelInput(project_id=project_id))
    return ApiResponse[DataModelResponse](
        message="Lấy mô hình dữ liệu thành công.",
        data=DataModelResponse.model_validate(result.model_dump()),
    )


@router.get(
    "/data-models/{data_model_id}/ddl",
    response_model=ApiResponse[DdlGenerationResponse],
    summary="Sinh mã DDL từ mô hình dữ liệu theo hệ quản trị CSDL đã chọn",
)
async def generate_data_model_ddl(
    data_model_id: UUID,
    use_case: GenerateDdlUseCase,
    dialect: SqlDialect = Query(
        default=SqlDialect.POSTGRESQL,
        description="Hệ quản trị CSDL đích của script DDL",
    ),
    schema_name: str | None = Query(
        default=None,
        description="Tên schema Sandbox tùy chọn; bỏ trống sẽ dùng schema mặc định",
    ),
) -> ApiResponse[DdlGenerationResponse]:
    """Trả về script DDL đã gắn tiền tố schema Sandbox, sẵn sàng để tải về dạng `.sql`."""
    payload = GenerateDdlInput(
        data_model_id=data_model_id,
        dialect=dialect,
        schema_name=schema_name,
    )
    result = await use_case.execute(payload)
    return ApiResponse[DdlGenerationResponse](
        message="Sinh mã DDL thành công.",
        data=DdlGenerationResponse.model_validate(result.model_dump()),
    )


@router.get(
    "/data-models/{data_model_id}/changes",
    response_model=ApiResponse[list[ChangeProposalSummaryResponse]],
    summary="Liệt kê đề xuất thay đổi của một mô hình dữ liệu",
)
async def list_data_model_changes(
    data_model_id: UUID,
    use_case: ListChangeProposalsUseCase,
    status: DataModelChangeStatus | None = Query(
        default=None,
        description="Lọc theo trạng thái đề xuất; bỏ trống sẽ lấy tất cả",
    ),
) -> ApiResponse[list[ChangeProposalSummaryResponse]]:
    """Trả về danh sách đề xuất thay đổi của mô hình dữ liệu, mới nhất trước."""
    payload = ListChangeProposalsInput(data_model_id=data_model_id, status=status)
    results = await use_case.execute(payload)
    return ApiResponse[list[ChangeProposalSummaryResponse]](
        message="Lấy danh sách đề xuất thay đổi thành công.",
        data=[ChangeProposalSummaryResponse.model_validate(item.model_dump()) for item in results],
    )
