"""Output model cho các thao tác Data Model."""

from dataclasses import dataclass
from datetime import datetime

from src.domain.data_model.entities import DataModel
from src.domain.shared.types import EntityID


@dataclass(frozen=True)
class DataModelOutput:
    """Snapshot Data Model được phép đi qua application boundary."""

    id: EntityID
    project_id: EntityID
    dbml: str
    revision: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, data_model: DataModel) -> "DataModelOutput":
        """Ánh xạ domain entity sang application output."""
        return cls(
            id=data_model.id,
            project_id=data_model.project_id,
            dbml=data_model.dbml,
            revision=data_model.revision,
            created_at=data_model.created_at,
            updated_at=data_model.updated_at,
        )


@dataclass(frozen=True)
class DataModelDdlOutput:
    """DDL được sinh từ một revision Data Model cụ thể."""

    ddl: str
    dialect: str
    revision: int


@dataclass(frozen=True)
class DataModelInsightOutput:
    """Một nhận xét cấu trúc được sinh từ DBML hiện tại."""

    id: str
    table_name: str
    severity: str
    title: str
    description: str
