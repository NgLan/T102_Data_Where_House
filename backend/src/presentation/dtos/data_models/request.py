"""Request schemas và parameter constraints cho API Data Model."""

from typing import Annotated
from uuid import UUID

from fastapi import Path
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_core import PydanticCustomError
from src.application.data_models.input import UpdateDataModelInput, ValidateDataModelInput
from src.common.exceptions.business import BusinessException
from src.domain.data_model.dbml_syntax_rules import validate_dbml

MAX_DBML_LENGTH = 1_000_000
MIN_INSTRUCTION_LENGTH = 5
MAX_INSTRUCTION_LENGTH = 2_000


class ValidateDataModelRequest(BaseModel):
    """Payload kiểm tra DBML draft mà không ghi dữ liệu."""

    model_config = ConfigDict(extra="forbid")
    dbml: str = Field(min_length=1, max_length=MAX_DBML_LENGTH, description="DBML draft cần kiểm tra")

    def to_application(self, project_id: UUID) -> ValidateDataModelInput:
        """Ánh xạ request sang application input."""
        return ValidateDataModelInput(project_id=project_id, dbml=self.dbml)
ProjectIdPath = Annotated[UUID, Path(description="ID dự án chứa Data Model")]


class UpdateDataModelRequest(BaseModel):
    """Payload lưu trực tiếp DBML với revision gốc của client."""

    model_config = ConfigDict(extra="forbid")

    data_model_id: UUID = Field(
        description="ID của Data Model cần cập nhật",
    )
    dbml: str = Field(
        min_length=1,
        max_length=MAX_DBML_LENGTH,
        description="Toàn bộ snapshot DBML mới",
    )
    base_revision: int = Field(
        ge=1,
        strict=True,
        description="Revision mà client đã tải trước khi chỉnh sửa",
    )

    @field_validator("dbml")
    @classmethod
    def validate_dbml_content(cls, value: str) -> str:
        """Kiểm tra đầy đủ nội dung DBML ngay tại HTTP request boundary."""
        try:
            validate_dbml(value)
        except BusinessException as exc:
            raise PydanticCustomError(
                exc.code.value,
                exc.message,
            ) from exc
        return value

    def to_application(self, project_id: UUID) -> UpdateDataModelInput:
        """Ánh xạ request DTO sang application input."""
        return UpdateDataModelInput(
            project_id=project_id,
            data_model_id=self.data_model_id,
            dbml=self.dbml,
            base_revision=self.base_revision,
        )


class ReviseDataModelRequest(BaseModel):
    """Payload nhờ AI Agent chỉnh sửa mô hình dữ liệu bằng ngôn ngữ tự nhiên."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "instruction": "Tách bảng Dim_Driver thành Dim_Driver và Dim_Vehicle.",
            },
        },
    )

    instruction: str = Field(
        min_length=MIN_INSTRUCTION_LENGTH,
        max_length=MAX_INSTRUCTION_LENGTH,
        description="Yêu cầu chỉnh sửa mô hình dữ liệu, viết bằng ngôn ngữ tự nhiên",
    )
