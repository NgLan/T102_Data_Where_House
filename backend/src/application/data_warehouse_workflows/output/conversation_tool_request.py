"""Typed internal tool request emitted by the DW conversation Agent."""

from dataclasses import dataclass

from src.domain.data_model.enums import DataModelTargetKind
from src.domain.sandbox.enums import SandboxDbType
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class ConversationToolRequest:
    """Tool name and safe arguments before registry authorization."""

    name: str
    target_kind: DataModelTargetKind
    proposal_change_id: EntityID | None = None
    db_type: SandboxDbType = SandboxDbType.POSTGRESQL
    reset_schema: bool | None = None
