"""RequirementAgent gồm đúng clarification và analytical derivation."""

from src.application.requirements.i_requirement_service import IRequirementAnalysisAgent
from src.application.requirements.input import (
    ClarifyRequirementsInput,
    DeriveAnalyticalRequirementsInput,
    EvaluateSourceCoverageInput,
)
from src.application.requirements.output import (
    AnalyticalDerivationResult,
    RequirementClarificationResult,
    SourceCoverageResult,
)
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.project_session.enums import RequirementClarificationStatus
from src.infrastructure.agents.agent_context_renderer import (
    render_analytical_input,
    render_source_coverage_input,
)
from src.infrastructure.agents.prompts.requirement import (
    ANALYTICAL_SYSTEM_PROMPT,
    ANALYTICAL_USER_PROMPT,
    REQUIREMENT_CLARIFICATION_SYSTEM_PROMPT,
    REQUIREMENT_CLARIFICATION_USER_PROMPT,
    SOURCE_COVERAGE_SYSTEM_PROMPT,
    SOURCE_COVERAGE_USER_PROMPT,
)
from src.infrastructure.agents.requirement_agent_output_mapper import (
    map_derivation_outcome,
    map_requirement_items,
)
from src.infrastructure.agents.requirement_context_renderer import render_requirement_clarification
from src.infrastructure.agents.source_coverage_output_mapper import (
    map_source_coverage_result,
)
from src.infrastructure.llm.agent_structured_outputs import (
    AnalyticalRequirementResult,
    SourceCoverageLlmResult,
)
from src.infrastructure.llm.agent_structured_outputs import (
    RequirementClarificationResult as RequirementClarificationLlmResult,
)
from src.infrastructure.llm.lazy_chat_model import ChatModelSource, LazyChatModel
from src.infrastructure.llm.structured_llm_invoker import StructuredLlmInvoker
from src.infrastructure.security.pii_guard import PiiGuard
from typing_extensions import override


class RequirementAnalysisAgent(IRequirementAnalysisAgent):
    """Adapter provider-neutral cho hai RequirementAgent operations."""

    def __init__(self, chat_model: ChatModelSource, pii_guard: PiiGuard) -> None:
        self._model = LazyChatModel(chat_model)
        self._pii_guard = pii_guard

    @override
    async def clarify_requirements(self, data: ClarifyRequirementsInput) -> RequirementClarificationResult:
        """Cấu trúc/làm rõ Requirement bằng một structured invocation."""
        sections = render_requirement_clarification(data)
        result = await self._invoker().invoke(
            REQUIREMENT_CLARIFICATION_SYSTEM_PROMPT,
            REQUIREMENT_CLARIFICATION_USER_PROMPT.format(**sections),
            RequirementClarificationLlmResult,
        )
        return RequirementClarificationResult(
            requirements=map_requirement_items(result.requirements, data),
            status=RequirementClarificationStatus(result.status),
            question=result.question,
            options=tuple(result.options),
            allow_custom_answer=result.allow_custom_answer,
            reason=result.reason,
            summary=result.summary,
        )

    @override
    async def derive_analytical_requirements(
        self, data: DeriveAnalyticalRequirementsInput
    ) -> AnalyticalDerivationResult:
        """Derive outcome đầy đủ với source ID bắt buộc thuộc input."""
        requirements = render_analytical_input(data)
        result = await self._invoker().invoke(
            ANALYTICAL_SYSTEM_PROMPT,
            ANALYTICAL_USER_PROMPT.format(requirements=requirements),
            AnalyticalRequirementResult,
        )
        expected_ids = {str(item.id) for item in data.requirements}
        actual_ids = [item.source_requirement_id for item in result.outcomes]
        if len(actual_ids) != len(expected_ids) or set(actual_ids) != expected_ids:
            raise InfrastructureException(
                ErrorCode.LLM_STRUCTURED_OUTPUT_ERROR,
                "RequirementAgent trả thiếu, trùng hoặc sai source_requirement_id.",
            )
        return AnalyticalDerivationResult(
            tuple(map_derivation_outcome(item) for item in result.outcomes)
        )

    @override
    async def evaluate_source_coverage(
        self, data: EvaluateSourceCoverageInput
    ) -> SourceCoverageResult:
        """Đánh giá source semantics bằng một invocation độc lập và grounded."""
        requirements, analytical, schemas = render_source_coverage_input(data)
        result = await self._invoker().invoke(
            SOURCE_COVERAGE_SYSTEM_PROMPT,
            SOURCE_COVERAGE_USER_PROMPT.format(
                requirements=requirements,
                analytical_requirements=analytical,
                schema_metadata=schemas,
            ),
            SourceCoverageLlmResult,
        )
        return map_source_coverage_result(result, data)

    def _invoker(self) -> StructuredLlmInvoker:
        """Dựng invoker nhẹ trên model đã lazy-cache."""
        return StructuredLlmInvoker(self._model.get(), self._pii_guard)
