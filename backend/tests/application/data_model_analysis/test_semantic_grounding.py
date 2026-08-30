"""Grounding and one-repair contract for Data Model analysis."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.data_model_analysis.data_model_analysis_service import DataModelAnalysisService
from src.application.data_model_analysis.models import (
    AnalysisSemanticInput,
    AnalysisSemanticOutput,
    EvidenceLevel,
    GenerateAnalysisDocumentInput,
    ModelColumn,
    ModelStructure,
    ModelTable,
    SemanticObservation,
)
from src.application.data_model_analysis.semantic_grounding import validate_semantic_output
from src.application.data_models.output import ResolvedDataModelTargetOutput
from src.domain.data_model.enums import DataModelTargetKind
from src.domain.project.entities import Project

from tests.fakes import FakeProjectMemberRepository, FakeProjectRepository


def _structure() -> ModelStructure:
    return ModelStructure(
        (ModelTable("Fact_Sales", (ModelColumn("amount", "numeric", False, False),)),),
        (),
    )


def test_unknown_reference_is_rejected_and_missing_evidence_is_downgraded() -> None:
    data = AnalysisSemanticInput(_structure(), (), (), "Sales", "vi")
    missing = AnalysisSemanticOutput(
        (SemanticObservation("Possible grain", EvidenceLevel.INFERRED),), ()
    )
    grounded = validate_semantic_output(data, missing)
    assert grounded.observations[0].evidence is EvidenceLevel.UNKNOWN

    hallucinated = AnalysisSemanticOutput(
        (SemanticObservation("Invented", EvidenceLevel.INFERRED, "Fact_Missing"),), ()
    )
    with pytest.raises(ValueError, match="unknown table"):
        validate_semantic_output(data, hallucinated)


@pytest.mark.asyncio
async def test_service_repairs_invalid_semantic_reference_once() -> None:
    project = Project(name="Sales", user_id=uuid4())
    model_id = uuid4()
    models = AsyncMock()
    models.resolve_target.return_value = ResolvedDataModelTargetOutput(
        project.id,
        "Table Fact_Sales { amount numeric }",
        3,
        DataModelTargetKind.CURRENT_MODEL,
        model_id,
    )
    models.validate_draft.return_value = ()
    requirements = AsyncMock()
    requirements.list_by_project.return_value = []
    analytical = AsyncMock()
    analytical.list_by_project.return_value = []
    sources = AsyncMock()
    sources.list_by_project.return_value = []
    extractor = MagicMock()
    extractor.extract.return_value = _structure()
    agent = AsyncMock()
    agent.analyze.return_value = AnalysisSemanticOutput(
        (SemanticObservation("Bad", EvidenceLevel.INFERRED, "Fact_Missing"),), ()
    )
    agent.repair.return_value = AnalysisSemanticOutput(
        (SemanticObservation("Sales measure", EvidenceLevel.INFERRED, "Fact_Sales"),), ()
    )
    access = ProjectAccessPolicy(
        FakeProjectRepository([project]), FakeProjectMemberRepository([]), project.user_id
    )
    service = DataModelAnalysisService(
        access, models, requirements, analytical, sources, extractor, agent
    )

    output = await service.generate_document(GenerateAnalysisDocumentInput(project.id))

    agent.analyze.assert_awaited_once()
    agent.repair.assert_awaited_once()
    assert "Sales measure" in output.content
    assert output.data_model_revision == 3
