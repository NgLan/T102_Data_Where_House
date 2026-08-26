"""Response payload DTO cho Project API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from src.application.projects.output import ProjectOutput, ProjectSummaryOutput
from src.domain.project.enums import ProjectStatus
from src.domain.requirement.enums import RequirementPriority, RequirementType
from src.presentation.dtos.data_sources.response import DataSourceResponse


class ProjectSummaryResponse(BaseModel):
    """Payload gọn cho danh sách Project."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="ID Project")
    name: str = Field(description="Tên Project")
    user_id: UUID = Field(description="ID người tạo Project")
    status: ProjectStatus = Field(description="Trạng thái Project")
    domain: str | None = Field(description="Lĩnh vực nghiệp vụ")
    description: str | None = Field(description="Mô tả Project")
    created_at: datetime = Field(description="Thời điểm tạo")
    updated_at: datetime = Field(description="Thời điểm cập nhật")
    data_source_count: int = Field(ge=0, description="Số nguồn dữ liệu thuộc Project")
    is_data_model_outdated: bool = Field(
        description="Data Model hiện hữu không còn khớp analysis revisions"
    )

    @classmethod
    def from_summary(cls, output: ProjectSummaryOutput) -> "ProjectSummaryResponse":
        """Ánh xạ application summary sang response payload.

        Args:
            output: Project summary do application layer trả về.

        Returns:
            Payload tóm tắt Project đã được Pydantic xác thực.
        """
        return cls.model_validate(output)


class ProjectResponse(BaseModel):
    """Payload chi tiết Project."""

    id: UUID = Field(description="ID Project")
    name: str = Field(description="Tên Project")
    user_id: UUID = Field(description="ID người tạo Project")
    status: ProjectStatus = Field(description="Trạng thái Project")
    domain: str | None = Field(description="Lĩnh vực nghiệp vụ")
    description: str | None = Field(description="Mô tả Project")
    created_at: datetime = Field(description="Thời điểm tạo")
    updated_at: datetime = Field(description="Thời điểm cập nhật")
    data_source_count: int = Field(ge=0, description="Số nguồn dữ liệu thuộc Project")
    requirement: str | None = Field(description="Yêu cầu nghiệp vụ thô")
    requirement_revision: int = Field(ge=0, description="Raw/document revision")
    analyzed_requirement_revision: int = Field(ge=0, description="Structured revision")
    derived_analytical_requirement_revision: int = Field(
        ge=0, description="Revision đã derive analytical requirements"
    )
    requirements: list["ProjectRequirementResponse"] = Field(description="Requirement đã được chuẩn hóa và phân loại")
    data_sources: list[DataSourceResponse] = Field(description="Nguồn dữ liệu")

    @classmethod
    def from_project(cls, output: ProjectOutput) -> "ProjectResponse":
        """Ánh xạ application output sang response payload.

        Args:
            output: Project chi tiết do application layer trả về.

        Returns:
            Payload chi tiết Project đã được Pydantic xác thực.
        """
        summary = output.summary
        return cls(
            id=summary.id,
            name=summary.name,
            requirement=output.requirement,
            requirement_revision=output.requirement_revision,
            analyzed_requirement_revision=output.analyzed_requirement_revision,
            derived_analytical_requirement_revision=(
                output.derived_analytical_requirement_revision
            ),
            user_id=summary.user_id,
            status=summary.status,
            domain=summary.domain,
            description=summary.description,
            created_at=summary.created_at,
            updated_at=summary.updated_at,
            data_source_count=summary.data_source_count,
            requirements=[ProjectRequirementResponse.model_validate(item) for item in output.requirements],
            data_sources=[DataSourceResponse.model_validate(item) for item in output.data_sources],
        )


class ProjectRequirementResponse(BaseModel):
    """Một hàng Requirement trong màn Project Init."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str
    type: RequirementType
    priority: RequirementPriority


class RawRequirementResponse(BaseModel):
    """Payload sau khi lưu Raw Requirement."""

    requirement: str | None = Field(description="Raw Requirement đã normalize")
    requirement_revision: int = Field(ge=0, description="Revision hiện hành")
