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
from src.domain.project_session.enums import RequirementClarificationStatus
from src.infrastructure.agents.analytical_output_retry import AnalyticalOutputRetry
from src.infrastructure.agents.clarification_output_retry import ClarificationOutputRetry
from src.infrastructure.agents.requirement_agent_output_mapper import (
    map_requirement_items,
)
from src.infrastructure.agents.source_coverage_output_retry import SourceCoverageOutputRetry
from src.infrastructure.agents.transport_references import (
    SourceCoverageReferenceBoundary,
    TransportReferenceMap,
)
from src.infrastructure.llm.lazy_chat_model import LazyLlmGateway, LlmGatewaySource
from src.infrastructure.llm.structured_llm_invoker import StructuredLlmInvoker
from src.infrastructure.security.pii_guard import PiiGuard
from typing_extensions import override


class RequirementAnalysisAgent(IRequirementAnalysisAgent):
    """Adapter provider-neutral cho hai RequirementAgent operations."""

    def __init__(
        self,
        gateway: LlmGatewaySource,
        pii_guard: PiiGuard,
        max_attempts: int = 3,
    ) -> None:
        self._gateway = LazyLlmGateway(gateway)
        self._pii_guard = pii_guard
        self._max_attempts = max_attempts

    @override
    async def clarify_requirements(self, data: ClarifyRequirementsInput) -> RequirementClarificationResult:
        """Cấu trúc/làm rõ Requirement bằng một structured invocation."""
        references = TransportReferenceMap.create("R", tuple(item.id for item in data.current_requirements))
        result = await ClarificationOutputRetry(self._invoker(), self._max_attempts).invoke(data, references)
        return RequirementClarificationResult(
            requirements=map_requirement_items(result.requirements, references),
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
        references = TransportReferenceMap.create("R", tuple(item.id for item in data.requirements))
        return await AnalyticalOutputRetry(self._invoker(), self._max_attempts).invoke(data, references)

    @override
    async def evaluate_source_coverage(self, data: EvaluateSourceCoverageInput) -> SourceCoverageResult:
        """Đánh giá source semantics bằng một invocation độc lập và grounded."""
        references = SourceCoverageReferenceBoundary(
            TransportReferenceMap.create("R", tuple(item.id for item in data.requirements)),
            TransportReferenceMap.create("A", tuple(item.id for item in data.analytical_requirements)),
            TransportReferenceMap.create("S", tuple(item.id for item in data.data_sources)),
        )
        return await SourceCoverageOutputRetry(self._invoker(), self._max_attempts).invoke(data, references)

    def _invoker(self) -> StructuredLlmInvoker:
        """Dựng invoker nhẹ trên model đã lazy-cache."""
        return StructuredLlmInvoker(self._gateway.get(), self._pii_guard)
