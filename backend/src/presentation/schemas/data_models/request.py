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
