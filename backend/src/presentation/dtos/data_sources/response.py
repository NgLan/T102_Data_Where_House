"""Response schemas ổn định cho Data Source API."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from src.application.data_sources.output import (
    DataSourceListOutput,
    DataSourceOutput,
    PreviewOutput,
    UploadDataSourcesOutput,
)
from src.domain.data_source.enums import (
    ColumnDataType,
    DataSourceAnalysisStatus,
    DataSourceType,
)
from src.domain.shared.types import JsonScalar
from src.presentation.dtos.data_sources.constraints import ColumnConstraintDto


class DataSourceColumnResponse(BaseModel):
    """Metadata một cột nguồn."""

    model_config = ConfigDict(from_attributes=True)
    name: str = Field(description="Tên cột")
    data_type: ColumnDataType = Field(description="Kiểu dữ liệu hiển thị")
    nullable: bool = Field(description="Cột cho phép NULL")
    primary_key: bool = Field(description="Cột là khóa chính")
    null_count: int = Field(default=0, ge=0, description="Số giá trị NULL quan sát được")
    distinct_count: int = Field(default=0, ge=0, description="Số giá trị phân biệt")
    distinct_values: list[JsonScalar] = Field(
        default_factory=list,
        description="Giá trị phân biệt phù hợp để hiển thị",
    )
    constraints: list[ColumnConstraintDto] = Field(
        default_factory=list,
        description="Constraint chính thức của cột",
    )
    is_unique_candidate: bool = Field(
        default=False,
        description="Cột có toàn bộ giá trị quan sát được là duy nhất",
    )
    is_key_candidate: bool = Field(
        default=False,
        description="Cột có profile phù hợp làm khóa ứng viên",
    )


class DataSourceTableResponse(BaseModel):
    """Metadata một bảng nguồn."""

    model_config = ConfigDict(from_attributes=True)
    name: str = Field(description="Tên bảng")
    columns: list[DataSourceColumnResponse] = Field(description="Danh sách cột")


class DataSourceResponse(BaseModel):
    """Nguồn dữ liệu hiển thị trên Frontend."""

    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(description="ID nguồn dữ liệu")
    project_id: UUID = Field(description="ID Project sở hữu")
    name: str = Field(description="Tên nguồn dữ liệu")
    type: DataSourceType = Field(description="Loại nguồn dữ liệu")
    description: str | None = Field(description="Mô tả nguồn dữ liệu")
    tables: list[DataSourceTableResponse] = Field(description="Metadata bảng")
    analysis_status: DataSourceAnalysisStatus = Field(
        description="Trạng thái phân tích metadata nguồn",
    )

    @classmethod
    def from_application(cls, output: DataSourceOutput) -> "DataSourceResponse":
        """Ánh xạ application output sang response DTO."""
        return cls.model_validate(output)


class DataSourcePreviewResponse(BaseModel):
    """Preview đọc lười từ file nguồn."""

    model_config = ConfigDict(from_attributes=True)
    table_name: str = Field(description="Table đang được preview")
    available_tables: list[str] = Field(description="Các table có trong source")
    rows: list[dict[str, str | None]] = Field(description="Các dòng preview")
    total_rows: int = Field(ge=0, description="Tổng số dòng")

    @classmethod
    def from_application(cls, output: PreviewOutput) -> "DataSourcePreviewResponse":
        """Ánh xạ preview output sang response DTO."""
        return cls.model_validate(output)


class DataSourceListResponse(BaseModel):
    """Danh sách nguồn kèm quyền chỉnh sửa của actor."""

    items: list[DataSourceResponse] = Field(description="Danh sách nguồn")
    can_edit: bool = Field(description="Actor có quyền chỉnh sửa")

    @classmethod
    def from_application(cls, output: DataSourceListOutput) -> "DataSourceListResponse":
        """Ánh xạ list output sang response DTO."""
        return cls(
            items=[DataSourceResponse.from_application(item) for item in output.items],
            can_edit=output.can_edit,
        )


class UploadDataSourcesResponse(BaseModel):
    """Kết quả một batch upload CSV."""

    data_sources: list[DataSourceResponse] = Field(description="Nguồn đã lưu")
    total_files_uploaded: int = Field(ge=0, description="Số file đã tải lên")

    @classmethod
    def from_application(cls, output: UploadDataSourcesOutput) -> "UploadDataSourcesResponse":
        """Ánh xạ upload output sang response DTO."""
        return cls(
            data_sources=[DataSourceResponse.from_application(item) for item in output.data_sources],
            total_files_uploaded=output.total_files_uploaded,
        )
