"""Response payload DTO cho Project API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from src.application.projects.output import ProjectOutput, ProjectSummaryOutput
from src.domain.data_source.enums import DataSourceType
from src.domain.project.enums import ProjectStatus


class ProjectColumnResponse(BaseModel):
    """Metadata cột nguồn trả về cho client."""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(description="Tên cột")
    data_type: str = Field(description="Kiểu dữ liệu")
    nullable: bool = Field(description="Cột cho phép NULL")
    primary_key: bool = Field(description="Cột là khóa chính")
    options: list[str] = Field(default_factory=list, description="Giá trị OPTION")


class ProjectTableResponse(BaseModel):
    """Metadata bảng nguồn trả về cho client."""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(description="Tên bảng")
    columns: list[ProjectColumnResponse] = Field(description="Danh sách cột")


class ProjectDataSourceResponse(BaseModel):
    """Nguồn dữ liệu thuộc Project, không chứa storage location."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="ID nguồn dữ liệu")
    project_id: UUID = Field(description="ID Project sở hữu")
    name: str = Field(description="Tên nguồn dữ liệu")
    type: DataSourceType = Field(description="Loại nguồn dữ liệu")
    description: str | None = Field(description="Mô tả nguồn dữ liệu")
    tables: list[ProjectTableResponse] = Field(description="Metadata bảng")


class ProjectSummaryResponse(BaseModel):
    """Payload gọn cho danh sách Project."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="ID Project")
    name: str = Field(description="Tên Project")
    requirement: str = Field(description="Yêu cầu nghiệp vụ")
    user_id: UUID = Field(description="ID người tạo Project")
    status: ProjectStatus = Field(description="Trạng thái Project")
    domain: str | None = Field(description="Lĩnh vực nghiệp vụ")
    description: str | None = Field(description="Mô tả Project")
    created_at: datetime = Field(description="Thời điểm tạo")
    updated_at: datetime = Field(description="Thời điểm cập nhật")
    data_source_count: int = Field(ge=0, description="Số nguồn dữ liệu thuộc Project")

    @classmethod
    def from_summary(cls, output: ProjectSummaryOutput) -> "ProjectSummaryResponse":
        """Ánh xạ application summary sang response payload.

        Args:
            output: Project summary do application layer trả về.

        Returns:
            Payload tóm tắt Project đã được Pydantic xác thực.
        """
        return cls.model_validate(output)


class ProjectResponse(ProjectSummaryResponse):
    """Payload chi tiết Project."""

    data_sources: list[ProjectDataSourceResponse] = Field(description="Nguồn dữ liệu")

    @classmethod
    def from_project(cls, output: ProjectOutput) -> "ProjectResponse":
        """Ánh xạ application output sang response payload.

        Args:
            output: Project chi tiết do application layer trả về.

        Returns:
            Payload chi tiết Project đã được Pydantic xác thực.
        """
        return cls.model_validate(output)
