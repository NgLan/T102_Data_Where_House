"""Response schemas ổn định cho Data Source API."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from src.application.data_sources.output import (
    DataSourceListOutput,
    DataSourceOutput,
    PreviewOutput,
    UploadDataSourcesOutput,
)


class DataSourceColumnResponse(BaseModel):
    """Metadata một cột nguồn."""

    model_config = ConfigDict(from_attributes=True)
    name: str
    data_type: str
    nullable: bool
    primary_key: bool
    options: list[str] = Field(default_factory=list)


class DataSourceTableResponse(BaseModel):
    """Metadata một bảng nguồn."""

    model_config = ConfigDict(from_attributes=True)
    name: str
    columns: list[DataSourceColumnResponse] = Field(default_factory=list)


class DataSourceResponse(BaseModel):
    """Nguồn dữ liệu hiển thị trên Frontend."""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    project_id: UUID
    name: str
    type: str
    description: str | None
    tables: list[DataSourceTableResponse] = Field(default_factory=list)

    @classmethod
    def from_application(cls, output: DataSourceOutput) -> "DataSourceResponse":
        """Ánh xạ application output sang response DTO."""
        return cls.model_validate(output)


class DataSourcePreviewResponse(BaseModel):
    """Preview đọc lười từ file nguồn."""

    model_config = ConfigDict(from_attributes=True)
    rows: list[dict[str, str | None]] = Field(default_factory=list)
    total_rows: int = Field(ge=0)

    @classmethod
    def from_application(cls, output: PreviewOutput) -> "DataSourcePreviewResponse":
        """Ánh xạ preview output sang response DTO."""
        return cls.model_validate(output)


class DataSourceListResponse(BaseModel):
    """Danh sách nguồn kèm quyền chỉnh sửa của actor."""

    items: list[DataSourceResponse] = Field(default_factory=list)
    can_edit: bool

    @classmethod
    def from_application(cls, output: DataSourceListOutput) -> "DataSourceListResponse":
        """Ánh xạ list output sang response DTO."""
        return cls(
            items=[DataSourceResponse.from_application(item) for item in output.items],
            can_edit=output.can_edit,
        )


class UploadDataSourcesResponse(BaseModel):
    """Kết quả một batch upload."""

    data_sources: list[DataSourceResponse] = Field(default_factory=list)
    extracted_requirement_text: str | None = None
    total_files_processed: int = Field(ge=0)

    @classmethod
    def from_application(cls, output: UploadDataSourcesOutput) -> "UploadDataSourcesResponse":
        """Ánh xạ upload output sang response DTO."""
        return cls(
            data_sources=[DataSourceResponse.from_application(item) for item in output.data_sources],
            extracted_requirement_text=output.extracted_requirement_text,
            total_files_processed=output.total_files_processed,
        )
