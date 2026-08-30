"""Application service sinh tài liệu phân tích từ canonical project state."""

from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.data_model_analysis.analysis_data import (
    AnalysisContext,
    AnalysisData,
    AnalysisPreparation,
)
from src.application.data_model_analysis.i_data_model_analysis_service import (
    IDataModelAnalysisAgent,
    IDataModelAnalysisService,
    IDataModelStructureExtractor,
)
from src.application.data_model_analysis.markdown_renderer import render_analysis_markdown
from src.application.data_model_analysis.models import (
    AnalysisDocumentOutput,
    AnalysisSemanticInput,
    AnalysisSemanticOutput,
    GenerateAnalysisDocumentInput,
)
from src.application.data_model_analysis.semantic_grounding import validate_semantic_output
from src.application.data_models.i_data_model_service import IDataModelService
from src.application.data_models.input import ResolveDataModelTargetInput, ValidateDataModelInput
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.analytical_requirement.i_analytical_requirement_repository import IAnalyticalRequirementRepository
from src.domain.data_source.i_data_source_repository import IDataSourceRepository
from src.domain.project.entities import Project
from src.domain.requirement.entities import Requirement
from src.domain.requirement.i_requirement_repository import IRequirementRepository
from typing_extensions import override


class DataModelAnalysisService(IDataModelAnalysisService):
    """Tập hợp evidence hiện hành rồi render tài liệu Markdown."""

    def __init__(
        self,
        access: ProjectAccessPolicy,
        models: IDataModelService,
        requirements: IRequirementRepository,
        analytical: IAnalyticalRequirementRepository,
        sources: IDataSourceRepository,
        extractor: IDataModelStructureExtractor,
        agent: IDataModelAnalysisAgent | None = None,
    ) -> None:
        self._access, self._models = access, models
        self._requirements, self._analytical = requirements, analytical
        self._sources, self._extractor = sources, extractor
        self._agent = agent

    @override
    async def generate_document(self, data: GenerateAnalysisDocumentInput) -> AnalysisDocumentOutput:
        project = (await self._access.require_member(data.project_id)).project
        target = await self._models.resolve_target(ResolveDataModelTargetInput(data.project_id, data.target))
        prepared = await self._prepare(data, project, target.dbml)
        semantic = await self._semantic_analysis(_semantic_input(prepared.context))
        analysis = AnalysisData(
            prepared.context,
            target.revision,
            target.kind,
            target.proposal_change_id,
            prepared.issues,
            semantic,
            target.current_revision or target.revision,
            target.base_revision or target.revision,
        )
        content = render_analysis_markdown(analysis)
        return AnalysisDocumentOutput(
            "data_warehouse_analysis.md",
            "text/markdown",
            content,
            target.revision,
            target.kind,
            target.proposal_change_id,
            target.current_revision or target.revision,
            target.base_revision or target.revision,
        )

    async def _prepare(self, data: GenerateAnalysisDocumentInput, project: Project, dbml: str) -> AnalysisPreparation:
        requirements = tuple(await self._requirements.list_by_project(data.project_id))
        analytical = tuple(await self._analytical.list_by_project(data.project_id))
        sources = tuple(await self._sources.list_by_project(data.project_id))
        structure = self._extractor.extract(dbml)
        issues = await self._models.validate_draft(ValidateDataModelInput(data.project_id, dbml))
        context = AnalysisContext(project, structure, requirements, analytical, sources, data.locale)
        return AnalysisPreparation(context, issues)

    async def _semantic_analysis(self, data: AnalysisSemanticInput) -> AnalysisSemanticOutput:
        if self._agent is None:
            return AnalysisSemanticOutput()
        try:
            return validate_semantic_output(data, await self._agent.analyze(data))
        except ValueError:
            return await self._repair(data)
        except InfrastructureException as exc:
            if exc.code is not ErrorCode.LLM_STRUCTURED_OUTPUT_ERROR:
                raise
            return await self._repair(data)

    async def _repair(self, data: AnalysisSemanticInput) -> AnalysisSemanticOutput:
        if self._agent is None:
            return AnalysisSemanticOutput()
        repaired = await self._agent.repair(
            data, "Use only canonical table, column, requirement and source references."
        )
        return validate_semantic_output(data, repaired)


def _semantic_input(context: AnalysisContext) -> AnalysisSemanticInput:
    return AnalysisSemanticInput(
        context.structure,
        tuple(item.id for item in context.requirements),
        tuple(item.id for item in context.sources),
        _project_context(context.project, context.requirements, context.analytical),
        context.locale,
    )


def _project_context(
    project: Project,
    requirements: tuple[Requirement, ...],
    analytical: tuple[AnalyticalRequirement, ...],
) -> str:
    requirement_text = "; ".join(f"{item.id}: {item.title} — {item.description}" for item in requirements)
    analytical_text = "; ".join(f"{item.metric} / {item.dimension} / {item.grain}" for item in analytical)
    return (
        f"Project: {project.name}. Goal: {project.description or project.requirement or ''}. "
        f"Requirements: {requirement_text}. Analytical requirements: {analytical_text}."
    )
