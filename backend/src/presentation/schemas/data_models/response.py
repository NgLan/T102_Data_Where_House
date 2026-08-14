"""Response schema của API Data Model."""

from pydantic import BaseModel, ConfigDict
from src.domain.data_model.enums import DdlDialect


class DdlDocumentResponse(BaseModel):
    """Mã DDL cùng metadata của phiên bản mô hình nguồn."""

    model_config = ConfigDict(from_attributes=True)

    model_name: str
    revision: int
    dialect: DdlDialect
    content: str
    table_count: int
    generated_at: str
