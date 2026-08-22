"""Module quản lý Mô hình Dữ liệu (Data Model Domain)."""

from src.domain.data_model.data_model_change_rules import (
    validate_change_status_transition,
    validate_revision_match,
)
from src.domain.data_model.dbml_syntax_rules import validate_dbml
from src.domain.data_model.entities import DataModel, DataModelChange
from src.domain.data_model.enums import DataModelChangeStatus
from src.domain.data_model.i_data_model_change_repository import IDataModelChangeRepository
from src.domain.data_model.i_data_model_repository import IDataModelRepository

__all__: list[str] = [
    "DataModel",
    "DataModelChange",
    "DataModelChangeStatus",
    "IDataModelRepository",
    "IDataModelChangeRepository",
    "validate_dbml",
    "validate_revision_match",
    "validate_change_status_transition",
]
