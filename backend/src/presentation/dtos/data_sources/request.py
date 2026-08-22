"""Request schemas và path constraints cho Data Source API."""

from typing import Annotated
from uuid import UUID

from fastapi import Path
from pydantic import BaseModel, ConfigDict, Field, model_validator
from src.application.data_sources.input import (
    DataSourceColumnTargetInput,
    UpdateDataSourceColumnInput,
)
from src.domain.data_source.enums import ColumnDataType
from src.domain.shared.types import JsonScalar
from src.presentation.dtos.data_sources.constraints import ColumnConstraintDto

ProjectIdPath = Annotated[UUID, Path(description="ID dự án chứa nguồn dữ liệu")]
SourceIdPath = Annotated[UUID, Path(description="ID nguồn dữ liệu")]
TableNamePath = Annotated[str, Path(min_length=1, max_length=255, description="Tên bảng")]
ColumnNamePath = Annotated[str, Path(min_length=1, max_length=255, description="Tên cột")]


class UpdateDataSourceColumnRequest(BaseModel):
    """Payload cập nhật một phần metadata cột."""

    model_config = ConfigDict(extra="forbid")

    data_type: ColumnDataType | None = Field(default=None, description="Kiểu hiển thị mới")
    distinct_values: list[JsonScalar] | None = Field(
        default=None,
        max_length=200,
        description="Tập giá trị phân biệt cần hiển thị",
    )
    constraints: list[ColumnConstraintDto] | None = Field(
        default=None,
        description="Danh sách constraint chính thức của cột",
    )

    @model_validator(mode="after")
    def require_change(self) -> "UpdateDataSourceColumnRequest":
        """Yêu cầu body chứa ít nhất một field cần cập nhật."""
        if not self.model_fields_set:
            raise ValueError("Cần cung cấp ít nhất một field metadata để cập nhật.")
        return self

    def to_application(
        self,
        target: DataSourceColumnTargetInput,
    ) -> UpdateDataSourceColumnInput:
        """Ánh xạ partial request sang application input."""
        return UpdateDataSourceColumnInput(
            target=target,
            data_type=self.data_type,
            distinct_values=(tuple(self.distinct_values) if self.distinct_values is not None else None),
            constraints=(
                tuple(item.to_application() for item in self.constraints) if self.constraints is not None else None
            ),
        )
