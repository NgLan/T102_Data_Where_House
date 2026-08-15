"""Request schemas và parameter constraints cho API Data Model."""

from typing import Annotated
from uuid import UUID

from fastapi import Path
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_core import PydanticCustomError
from src.application.data_models.input import UpdateDataModelInput
from src.common.exceptions.business import BusinessException
from src.domain.data_model.rules import validate_dbml

MAX_DBML_LENGTH = 1_000_000
ProjectIdPath = Annotated[UUID, Path(description="ID dự án chứa Data Model")]


class UpdateDataModelRequest(BaseModel):
    """Payload lưu snapshot DBML với revision gốc của client."""

    model_config = ConfigDict(extra="forbid")

    data_model_id: UUID = Field(description="ID của Data Model cần cập nhật")
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
