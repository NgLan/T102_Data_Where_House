"""Per-Analytical salvage và bounded retry cho Source Coverage."""

from src.application.requirements.input import EvaluateSourceCoverageInput
from src.application.requirements.output import SourceCoverageResult
from src.infrastructure.agents.prompts.requirement import (
    SOURCE_COVERAGE_SYSTEM_PROMPT,
    SOURCE_COVERAGE_USER_PROMPT,
)
from src.infrastructure.agents.source_coverage_context_renderer import render_source_coverage_input
from src.infrastructure.agents.source_coverage_output_mapper import (
    SourceCoverageMappingContext,
)
from src.infrastructure.agents.source_coverage_retry_consumer import consume_source_response
from src.infrastructure.agents.source_coverage_retry_state import SourceCoverageRetryState
from src.infrastructure.agents.structured_output_retry_reporting import (
    StructuredIssueLogContext,
    log_structured_issue,
    raise_structured_failure,
)
from src.infrastructure.agents.structured_retry_prompt import append_retry_feedback
from src.infrastructure.agents.transport_references import (
    SourceCoverageReferenceBoundary,
    TransportReferenceMap,
)
from src.infrastructure.llm.agent_structured_outputs import SourceCoverageLlmResult
from src.infrastructure.llm.structured_llm_invoker import StructuredLlmInvoker


class SourceCoverageOutputRetry:
    """Chỉ retry Analytical Requirement chưa pass grounding đầy đủ."""

    def __init__(self, invoker: StructuredLlmInvoker, max_attempts: int) -> None:
        self._invoker = invoker
        self._max_attempts = max_attempts

    async def invoke(
        self,
        data: EvaluateSourceCoverageInput,
        references: SourceCoverageReferenceBoundary,
    ) -> SourceCoverageResult:
        """Salvage grounded outcomes và không persist partial result."""
        state = SourceCoverageRetryState(
            data,
            references,
            SourceCoverageMappingContext.create(data, references),
            set(references.analytical_requirements.references),
            {},
        )
        for attempt in range(1, self._max_attempts + 1):
            result = await self._attempt(state, attempt)
            if result is not None:
                return result
        raise_structured_failure(state.last_issue)

    async def _attempt(
        self,
        state: SourceCoverageRetryState,
        attempt: int,
    ) -> SourceCoverageResult | None:
        analytical_refs = state.references.analytical_requirements
        attempt_input = self._subset(state.data, analytical_refs, state.pending)
        rendered = render_source_coverage_input(attempt_input, state.references)
        base = SOURCE_COVERAGE_USER_PROMPT.format(
            requirements=rendered[0],
            analytical_requirements=rendered[1],
            schema_metadata=rendered[2],
        )
        prompt = append_retry_feedback(base, state.issues) if state.issues else base
        response = await self._invoker.invoke_payload(SOURCE_COVERAGE_SYSTEM_PROMPT, prompt, SourceCoverageLlmResult)
        state.issues = consume_source_response(response, state)
        context = StructuredIssueLogContext("evaluate_source_coverage", attempt, response.metadata)
        for issue in state.issues:
            log_structured_issue(context, issue)
        state.last_issue = state.issues[-1] if state.issues else response.issue
        return self._complete_result(state)

    @staticmethod
    def _complete_result(state: SourceCoverageRetryState) -> SourceCoverageResult | None:
        if state.pending:
            return None
        references = state.references.analytical_requirements.references
        return SourceCoverageResult(tuple(state.accepted[reference] for reference in references))

    @staticmethod
    def _subset(
        data: EvaluateSourceCoverageInput,
        analytical_refs: TransportReferenceMap,
        pending: set[str],
    ) -> EvaluateSourceCoverageInput:
        analytical = tuple(
            item for item in data.analytical_requirements if analytical_refs.reference_for(item.id) in pending
        )
        requirement_ids = {item.requirement_id for item in analytical}
        requirements = tuple(item for item in data.requirements if item.id in requirement_ids)
        return EvaluateSourceCoverageInput(requirements, analytical, data.data_sources)
