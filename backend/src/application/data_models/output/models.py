"""Public output models của Data Model application service."""

from dataclasses import dataclass
from datetime import datetime

from src.domain.data_model.entities import DataModel, DataModelChange
from src.domain.data_model.enums import DataModelChangeStatus
from src.domain.sandbox.enums import SandboxDbType
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class DataModelOutput:
    id: EntityID
    project_id: EntityID
    dbml: str
    revision: int
    created_at: datetime
    updated_at: datetime
    is_outdated: bool = False

    @classmethod
    def from_domain(cls, model: DataModel, is_outdated: bool = False) -> "DataModelOutput":
        """Ánh xạ Data Model entity sang output."""
        return cls(
            model.id,
            model.project_id,
            model.dbml,
            model.revision,
            model.created_at,
            model.updated_at,
            is_outdated,
        )


@dataclass(frozen=True, slots=True)
class ChangeProposalSummaryOutput:
    id: EntityID
    data_model_id: EntityID
    user_id: EntityID
    base_revision: int
    status: DataModelChangeStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, change: DataModelChange) -> "ChangeProposalSummaryOutput":
        """Ánh xạ change entity sang summary output."""
        return cls(
            change.id,
            change.data_model_id,
            change.user_id,
            change.base_revision,
            change.status,
            change.created_at,
            change.updated_at,
        )


@dataclass(frozen=True, slots=True)
class ChangeProposalDetailOutput:
    summary: ChangeProposalSummaryOutput
    proposed_dbml: str
    current_dbml: str
    current_revision: int
    is_outdated: bool

    @classmethod
    def from_domain(
        cls,
        change: DataModelChange,
        model: DataModel,
    ) -> "ChangeProposalDetailOutput":
        """Ghép proposal với snapshot Data Model hiện hành."""
        return cls(
            summary=ChangeProposalSummaryOutput.from_domain(change),
            proposed_dbml=change.proposed_dbml,
            current_dbml=change.base_dbml,
            current_revision=model.revision,
            is_outdated=change.base_revision != model.revision,
        )


@dataclass(frozen=True, slots=True)
class DataModelDdlOutput:
    """DDL sinh từ một revision Data Model cụ thể."""

    ddl: str
    db_type: SandboxDbType
    data_model_revision: int
