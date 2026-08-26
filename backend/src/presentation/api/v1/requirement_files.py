"""REST endpoints cho Requirement Documents."""

from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, File, Form, Query, Response, UploadFile
from src.application.requirement_files.input import (
    DeleteRequirementFileInput,
    ListRequirementFilesInput,
    RequirementUploadInput,
    UploadRequirementFilesInput,
)
from src.application.requirement_files.requirement_file_service import (
    MAX_REQUIREMENT_FILE_SIZE,
)
from src.presentation.dependencies.requirement_files import (
    RequirementFileServiceDependency,
)
from src.presentation.dtos.requirement_files.request import (
    ProjectIdPath,
    RequirementFileIdPath,
)
from src.presentation.dtos.requirement_files.response import (
    RequirementFileListResponse,
    UploadRequirementFilesResponse,
)
from src.presentation.routing import ApiResponseRoute, error_responses

router = APIRouter(
    prefix="/projects/{project_id}/requirement-files",
    tags=["Requirement Files"],
    route_class=ApiResponseRoute,
)


@router.get(
    "",
    response_model=RequirementFileListResponse,
    operation_id="listProjectRequirementFiles",
    responses=error_responses(401, 403, 404, 422, 500),
)
async def list_requirement_files(
    project_id: ProjectIdPath,
    service: RequirementFileServiceDependency,
) -> RequirementFileListResponse:
    """Liệt kê metadata documents cho Project member."""
    output = await service.list_files(ListRequirementFilesInput(project_id))
    return RequirementFileListResponse.from_application(output)


@router.post(
    "/upload",
    response_model=UploadRequirementFilesResponse,
    status_code=HTTPStatus.CREATED,
    operation_id="uploadProjectRequirementFiles",
    responses=error_responses(401, 403, 404, 413, 422, 500),
)
async def upload_requirement_files(
    project_id: ProjectIdPath,
    service: RequirementFileServiceDependency,
    files: Annotated[list[UploadFile], File(description="Tối đa 20 documents")],
    expected_revision: Annotated[int, Form(ge=0)],
) -> UploadRequirementFilesResponse:
    """Parse và upload/replace một batch documents cho Project owner."""
    items = tuple(
        RequirementUploadInput(
            item.filename or "unknown",
            await item.read(MAX_REQUIREMENT_FILE_SIZE + 1),
        )
        for item in files
    )
    output = await service.upload_files(
        UploadRequirementFilesInput(project_id, items, expected_revision)
    )
    return UploadRequirementFilesResponse.from_application(output)


@router.delete(
    "/{file_id}",
    response_model=None,
    status_code=HTTPStatus.NO_CONTENT,
    operation_id="deleteProjectRequirementFile",
    responses=error_responses(401, 403, 404, 422, 500),
)
async def delete_requirement_file(
    project_id: ProjectIdPath,
    file_id: RequirementFileIdPath,
    service: RequirementFileServiceDependency,
    expected_revision: Annotated[int, Query(ge=0)],
) -> Response:
    """Xóa document và tăng shared Requirement revision."""
    await service.delete_file(
        DeleteRequirementFileInput(project_id, file_id, expected_revision)
    )
    return Response(status_code=HTTPStatus.NO_CONTENT)
