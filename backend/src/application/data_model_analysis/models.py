"""Typed input/output cho capability phân tích Data Warehouse."""

from dataclasses import dataclass
from enum import StrEnum

from src.application.data_models.input import DataModelTargetInput
from src.domain.data_model.enums import DataModelTargetKind
from src.domain.shared.types import EntityID


class EvidenceLevel(StrEnum):
    CONFIRMED = "CONFIRMED"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"


class RequirementCoverage(StrEnum):
    FULL = "FULL"
    PARTIAL = "PARTIAL"
    NOT_MET = "NOT_MET"


@dataclass(frozen=True, slots=True)
class GenerateAnalysisDocumentInput:
    project_id: EntityID
    target: DataModelTargetInput = DataModelTargetInput()
    locale: str = "vi"


@dataclass(frozen=True, slots=True)
class ModelColumn:
    name: str
    data_type: str
    is_primary_key: bool
    is_foreign_key: bool


@dataclass(frozen=True, slots=True)
class ModelTable:
    name: str
    columns: tuple[ModelColumn, ...]
    note: str = ""


@dataclass(frozen=True, slots=True)
class ModelRelationship:
    source: str
    target: str
    cardinality: str


@dataclass(frozen=True, slots=True)
class ModelStructure:
    tables: tuple[ModelTable, ...]
    relationships: tuple[ModelRelationship, ...]


@dataclass(frozen=True, slots=True)
class AnalysisDocumentOutput:
    filename: str
    mime_type: str
    content: str
    data_model_revision: int
    target_kind: DataModelTargetKind
    proposal_change_id: EntityID | None = None
    current_revision: int | None = None
    base_revision: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "current_revision", self.current_revision or self.data_model_revision)
        object.__setattr__(self, "base_revision", self.base_revision or self.data_model_revision)


@dataclass(frozen=True, slots=True)
class AnalysisSemanticInput:
    structure: ModelStructure
    requirement_ids: tuple[EntityID, ...]
    source_ids: tuple[EntityID, ...]
    project_context: str
    locale: str


@dataclass(frozen=True, slots=True)
class SemanticObservation:
    explanation: str
    evidence: EvidenceLevel
    table_name: str | None = None
    column_name: str | None = None
    requirement_id: EntityID | None = None
    source_id: EntityID | None = None


@dataclass(frozen=True, slots=True)
class AnalysisSemanticOutput:
    observations: tuple[SemanticObservation, ...] = ()
    uncertainties: tuple[str, ...] = ()
