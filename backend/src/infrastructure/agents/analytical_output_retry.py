"""Per-Requirement salvage và bounded retry cho analytical derivation."""

from dataclasses import dataclass

from src.application.requirements.input import DeriveAnalyticalRequirementsInput
from src.application.requirements.output import (
    AnalyticalDerivationOutcome,
    AnalyticalDerivationResult,
)
from src.infrastructure.agents.agent_context_renderer import render_analytical_input
from src.infrastructure.agents.prompts.requirement import (
    ANALYTICAL_SYSTEM_PROMPT,
    ANALYTICAL_USER_PROMPT,
)
from src.infrastructure.agents.requirement_agent_output_mapper import map_derivation_outcome
from src.infrastructure.agents.structured_output_retry_reporting import (
    StructuredIssueLogContext,
    log_structured_issue,
    raise_structured_failure,
)
from src.infrastructure.agents.structured_output_retry_support import (
    OutcomeValidationSpec,
    validate_outcome_batch,
)
from src.infrastructure.agents.structured_retry_prompt import append_retry_feedback
from src.infrastructure.agents.transport_references import TransportReferenceMap
from src.infrastructure.llm.agent_structured_outputs import (
    AnalyticalDerivationOutcome as AnalyticalLlmOutcome,
)
from src.infrastructure.llm.agent_structured_outputs import AnalyticalRequirementResult
from src.infrastructure.llm.structured_llm_invoker import StructuredLlmInvoker
from src.infrastructure.llm.structured_output_models import (
    StructuredOutputFailureCategory as Category,
)
from src.infrastructure.llm.structured_output_models import (
    StructuredOutputIssue,
    StructuredPayloadResult,
)

_REF_CATEGORIES = (
    Category.REQUIREMENT_REF_MISSING,
    Category.REQUIREMENT_REF_DUPLICATED,
    Category.REQUIREMENT_REF_UNKNOWN,
)


class AnalyticalOutputRetry:
    """Chỉ retry Requirement chưa có outcome hoàn toàn hợp lệ."""

    def __init__(self, invoker: StructuredLlmInvoker, max_attempts: int) -> None:
        self._invoker = invoker
        self._max_attempts = max_attempts

    async def invoke(
        self,
        data: DeriveAnalyticalRequirementsInput,
        references: TransportReferenceMap,
    ) -> AnalyticalDerivationResult:
        """Salvage outcomes hợp lệ và merge theo canonical input order."""
        state = _RetryState(data, references, set(references.references), {})
        for attempt in range(1, self._max_attempts + 1):
            result = await self._attempt(state, attempt)
            if result is not None:
                return result
        raise_structured_failure(state.last_issue)

    async def _attempt(
        self,
        state: "_RetryState",
        attempt: int,
    ) -> AnalyticalDerivationResult | None:
        attempt_input = self._subset(state.data, state.references, state.pending)
        rendered = render_analytical_input(attempt_input, state.references)
        base = ANALYTICAL_USER_PROMPT.format(requirements=rendered)
        prompt = append_retry_feedback(base, state.issues) if state.issues else base
        response = await self._invoker.invoke_payload(ANALYTICAL_SYSTEM_PROMPT, prompt, AnalyticalRequirementResult)
        state.issues = self._consume(response, state)
        context = StructuredIssueLogContext("derive_analytical_requirements", attempt, response.metadata)
        for issue in state.issues:
            log_structured_issue(context, issue)
        state.last_issue = state.issues[-1] if state.issues else response.issue
        return self._complete_result(state)

    @staticmethod
    def _consume(
        response: StructuredPayloadResult,
        state: "_RetryState",
    ) -> tuple[StructuredOutputIssue, ...]:
        if response.payload is None:
            return (response.issue,) if response.issue else ()
        spec = OutcomeValidationSpec("requirement_ref", frozenset(state.pending), _REF_CATEGORIES)
        batch = validate_outcome_batch(response.payload, AnalyticalLlmOutcome, spec)
        for reference, value in batch.values.items():
            identifier = state.references.resolve(reference)
            if isinstance(value, AnalyticalLlmOutcome) and identifier is not None:
                state.accepted[reference] = map_derivation_outcome(value, identifier)
                state.pending.discard(reference)
        return batch.issues

    @staticmethod
    def _complete_result(state: "_RetryState") -> AnalyticalDerivationResult | None:
        if state.pending:
            return None
        ordered = tuple(state.accepted[reference] for reference in state.references.references)
        return AnalyticalDerivationResult(ordered)

    @staticmethod
    def _subset(
        data: DeriveAnalyticalRequirementsInput,
        references: TransportReferenceMap,
        pending: set[str],
    ) -> DeriveAnalyticalRequirementsInput:
        requirements = tuple(item for item in data.requirements if references.reference_for(item.id) in pending)
        return DeriveAnalyticalRequirementsInput(requirements)


@dataclass(slots=True)
class _RetryState:
    data: DeriveAnalyticalRequirementsInput
    references: TransportReferenceMap
    pending: set[str]
    accepted: dict[str, AnalyticalDerivationOutcome]
    issues: tuple[StructuredOutputIssue, ...] = ()
    last_issue: StructuredOutputIssue | None = None
