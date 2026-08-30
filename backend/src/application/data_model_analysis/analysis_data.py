"""Canonical evidence bundle passed from analysis orchestration to rendering."""

from dataclasses import dataclass

from src.application.data_model_analysis.models import (
    AnalysisSemanticOutput,
    ModelStructure,
)
from src.application.data_warehouse_workflows.output import ValidationIssue
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.data_model.enums import DataModelTargetKind
from src.domain.data_source.entities import DataSource
from src.domain.project.entities import Project
from src.domain.requirement.entities import Requirement
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class AnalysisContext:
    project: Project
    structure: ModelStructure
    requirements: tuple[Requirement, ...]
    analytical: tuple[AnalyticalRequirement, ...]
    sources: tuple[DataSource, ...]
    locale: str


@dataclass(frozen=True, slots=True)
class AnalysisData:
    context: AnalysisContext
    revision: int
    target_kind: DataModelTargetKind
    proposal_change_id: EntityID | None
    issues: tuple[ValidationIssue, ...]
    semantic: AnalysisSemanticOutput = AnalysisSemanticOutput()
    current_revision: int | None = None
    base_revision: int | None = None


@dataclass(frozen=True, slots=True)
class AnalysisPreparation:
    context: AnalysisContext
    issues: tuple[ValidationIssue, ...]
