"""REST endpoints cho Data Model hiện tại của dự án."""

from uuid import UUID
from fastapi import APIRouter
from src.application.data_models.input import GetDataModelInput
from src.presentation.dependencies.data_models import DataModelServiceDependency
from src.presentation.dtos.common import ApiErrorResponse
from src.presentation.dtos.data_models.request import (
    ProjectIdPath,
    UpdateDataModelRequest,
)
from src.presentation.dtos.data_models.response import DataModelResponse
from src.presentation.routing import ApiResponseRoute

from fastapi import APIRouter, Query
from src.application.data_models.dto import (
    GenerateDdlInput,
    GetDataModelInput,
    ListChangeProposalsInput,
    ReviseDataModelInput,
)
from src.common.dto.response import ApiResponse
from src.domain.data_model.enums import DataModelChangeStatus, SqlDialect
from src.presentation.dependencies.application import (
    CreateChangeProposalUseCase,
    GenerateDdlUseCase,
    GetDataModelUseCase,
    ListChangeProposalsUseCase,
)
from src.presentation.schemas.data_model_changes.response import (
    ChangeProposalDetailResponse,
    ChangeProposalSummaryResponse,
)
from src.presentation.schemas.data_models.request import ReviseDataModelRequest
from src.presentation.schemas.data_models.response import (
    DataModelResponse,
    DdlGenerationResponse,
)

router = APIRouter(
    prefix="/projects/{project_id}/data-model",
    tags=["Data Models"],
    route_class=ApiResponseRoute,
)


@router.get(
    "",
    response_model=DataModelResponse,
    operation_id="getDataModel",
    responses={
        404: {"model": ApiErrorResponse},
        422: {"model": ApiErrorResponse},
        500: {"model": ApiErrorResponse},
    },
)
async def get_current_data_model(
    project_id: ProjectIdPath,
    service: DataModelServiceDependency,
) -> DataModelResponse:
    """Lấy DBML và revision hiện tại của dự án."""
    output = await service.get_data_model(GetDataModelInput(project_id=project_id))
    return DataModelResponse.from_application(output)


@router.put(
    "",
    response_model=DataModelResponse,
    operation_id="updateDataModel",
    responses={
        404: {"model": ApiErrorResponse},
        409: {"model": ApiErrorResponse},
        422: {"model": ApiErrorResponse},
        500: {"model": ApiErrorResponse},
    },
)
async def update_current_data_model(
    project_id: ProjectIdPath,
    request: UpdateDataModelRequest,
    service: DataModelServiceDependency,
) -> DataModelResponse:
    """Lưu snapshot DBML mới bằng optimistic locking."""
    output = await service.update_data_model(request.to_application(project_id))
    return DataModelResponse.from_application(output)
    
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


@router.post(
    "/data-models/{data_model_id}/ai-revisions",
    response_model=ApiResponse[ChangeProposalDetailResponse],
    summary="Nhờ AI Agent chỉnh sửa mô hình dữ liệu bằng ngôn ngữ tự nhiên",
)
async def revise_data_model_with_ai(
    data_model_id: UUID,
    payload: ReviseDataModelRequest,
    use_case: CreateChangeProposalUseCase,
) -> ApiResponse[ChangeProposalDetailResponse]:
    """Sinh DBML mới theo yêu cầu của người dùng và lưu thành đề xuất chờ duyệt."""
    result = await use_case.execute(
        ReviseDataModelInput(
            data_model_id=data_model_id,
            instruction=payload.instruction,
        )
    )
    return ApiResponse[ChangeProposalDetailResponse](
        message="AI Agent đã tạo đề xuất thay đổi thành công.",
        data=ChangeProposalDetailResponse.model_validate(result.model_dump()),
    )
