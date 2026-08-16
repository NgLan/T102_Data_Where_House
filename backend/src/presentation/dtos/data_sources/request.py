"""Request schemas và path constraints cho Data Source API."""

from typing import Annotated, Literal
from uuid import UUID

from fastapi import Path
from pydantic import BaseModel, ConfigDict, Field, field_validator
from src.application.data_sources.input import UpdateDataSourceColumnInput

ProjectIdPath = Annotated[UUID, Path(description="ID dự án chứa nguồn dữ liệu")]
DataSourceIdPath = Annotated[UUID, Path(description="ID nguồn dữ liệu")]
ColumnDataType = Literal["TEXT", "NUMBER", "DATETIME", "BOOLEAN", "OPTION"]


class UpdateDataSourceColumnRequest(BaseModel):
    """Payload chỉnh kiểu dữ liệu và options của một cột."""

    model_config = ConfigDict(extra="forbid")

    table_name: str = Field(min_length=1, max_length=255)
    column_name: str = Field(min_length=1, max_length=255)
    data_type: ColumnDataType
    options: list[str] = Field(default_factory=list, max_length=200)

    @field_validator("table_name", "column_name", mode="before")
    @classmethod
    def strip_name(cls, value: str) -> str:
        """Loại bỏ khoảng trắng thừa ở định danh schema."""
        return value.strip()

    def to_application(
        self,
        project_id: UUID,
        data_source_id: UUID,
    ) -> UpdateDataSourceColumnInput:
        """Ánh xạ request DTO sang application input."""
        return UpdateDataSourceColumnInput(
            project_id=project_id,
            data_source_id=data_source_id,
            table_name=self.table_name,
            column_name=self.column_name,
            data_type=self.data_type,
            options=tuple(self.options),
        )
