"""Input models độc lập HTTP cho Data Model application service."""

from dataclasses import dataclass

from src.domain.sandbox.enums import SandboxDbType
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class GetDataModelInput:
    project_id: EntityID


@dataclass(frozen=True, slots=True)
class ValidateDataModelInput:
    """DBML draft cần được kiểm tra mà không ghi snapshot."""

    project_id: EntityID
    dbml: str


@dataclass(frozen=True, slots=True)
class UpdateDataModelInput:
    project_id: EntityID
    data_model_id: EntityID
    dbml: str
    base_revision: int


@dataclass(frozen=True, slots=True)
class ChangeProposalIdInput:
    change_id: EntityID


@dataclass(frozen=True, slots=True)
class GetChangeProposalInput:
    """Input xem proposal trong phạm vi Project."""

    project_id: EntityID
    change_id: EntityID


@dataclass(frozen=True, slots=True)
class GetPendingChangeProposalInput:
    project_id: EntityID


@dataclass(frozen=True, slots=True)
class GenerateDataModelDdlInput:
    """Input sinh DDL từ Data Model hiện hành."""

    project_id: EntityID
    db_type: SandboxDbType = SandboxDbType.POSTGRESQL
