"""Module quản lý Mô hình Dữ liệu (Data Model Domain)."""

from src.domain.data_model.codegen import DdlGenerationResult, IDdlGenerator
from src.domain.data_model.entities import DataModel, DataModelChange
from src.domain.data_model.enums import DataModelChangeStatus, SqlDialect
from src.domain.data_model.repository import IDataModelChangeRepository, IDataModelRepository
from src.domain.data_model.rules import (
    validate_change_status_transition,
    validate_dbml,
    validate_revision_match,
)

__all__: list[str] = [
    "DataModel",
    "DataModelChange",
    "DataModelChangeStatus",
    "SqlDialect",
    "IDataModelRepository",
    "IDataModelChangeRepository",
    "IDdlGenerator",
    "DdlGenerationResult",
    "validate_dbml",
    "validate_revision_match",
    "validate_change_status_transition",
]
