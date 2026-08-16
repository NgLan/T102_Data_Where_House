"""Request schema của API Data Model."""

from pydantic import BaseModel, ConfigDict, Field
from src.domain.data_model.enums import DdlDialect


class ViewDdlRequest(BaseModel):
    """Yêu cầu sinh DDL từ mô hình đang mở trên frontend."""

    model_config = ConfigDict(str_strip_whitespace=True)

    model_name: str = Field(min_length=1, max_length=200)
    revision: int = Field(ge=1)
    dialect: DdlDialect = DdlDialect.POSTGRESQL
    dbml: str = Field(min_length=1, max_length=200_000)
"""Pydantic Request Schemas cho nhóm endpoint Mô hình Dữ liệu (Data Models)."""

from pydantic import BaseModel, ConfigDict, Field
from src.application.data_models.dto import (
    MAX_INSTRUCTION_LENGTH,
    MIN_INSTRUCTION_LENGTH,
)


class ReviseDataModelRequest(BaseModel):
    """Yêu cầu nhờ AI Agent chỉnh sửa mô hình dữ liệu bằng ngôn ngữ tự nhiên (T-024)."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "instruction": "Tách bảng Dim_Driver thành Dim_Driver và Dim_Vehicle."
            }
        }
    )

    instruction: str = Field(
        min_length=MIN_INSTRUCTION_LENGTH,
        max_length=MAX_INSTRUCTION_LENGTH,
        description="Yêu cầu chỉnh sửa mô hình dữ liệu, viết bằng ngôn ngữ tự nhiên",
    )
