"""Validate và salvage độc lập từng Source Coverage outcome."""

from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.infrastructure.agents.source_coverage_output_mapper import map_source_coverage_outcome
from src.infrastructure.agents.source_coverage_retry_state import SourceCoverageRetryState
from src.infrastructure.agents.structured_output_retry_support import (
    OutcomeValidationSpec,
    ValidatedOutcomeBatch,
    validate_outcome_batch,
)
from src.infrastructure.llm.source_coverage_structured_outputs import SourceCoverageOutcomeItem
from src.infrastructure.llm.structured_output_models import (
    StructuredOutputFailureCategory as Category,
)
from src.infrastructure.llm.structured_output_models import (
    StructuredOutputIssue,
    StructuredOutputItemError,
    StructuredPayloadResult,
)

_REF_CATEGORIES = (
    Category.ANALYTICAL_REF_MISSING,
    Category.ANALYTICAL_REF_DUPLICATED,
    Category.ANALYTICAL_REF_UNKNOWN,
)


def consume_source_response(
    response: StructuredPayloadResult,
    state: SourceCoverageRetryState,
) -> tuple[StructuredOutputIssue, ...]:
    """Validate batch identity rồi salvage các item grounded hoàn toàn."""
    if response.payload is None:
        return (response.issue,) if response.issue else ()
    spec = OutcomeValidationSpec("analytical_requirement_ref", frozenset(state.pending), _REF_CATEGORIES)
    batch = validate_outcome_batch(response.payload, SourceCoverageOutcomeItem, spec)
    return _map_valid_items(batch, state)


def _map_valid_items(
    batch: ValidatedOutcomeBatch,
    state: SourceCoverageRetryState,
) -> tuple[StructuredOutputIssue, ...]:
    issues = list(batch.issues)
    for reference, value in batch.values.items():
        if not isinstance(value, SourceCoverageOutcomeItem):
            continue
        try:
            state.accepted[reference] = map_source_coverage_outcome(value, state.mapping)
        except StructuredOutputItemError as exc:
            issues.append(exc.issue)
            continue
        except InfrastructureException as exc:
            issue = _semantic_issue(exc, reference)
            if issue is None:
                raise
            issues.append(issue)
            continue
        state.pending.discard(reference)
    return tuple(issues)


def _semantic_issue(
    exc: InfrastructureException,
    reference: str,
) -> StructuredOutputIssue | None:
    if exc.code is not ErrorCode.LLM_STRUCTURED_OUTPUT_ERROR:
        return None
    return StructuredOutputIssue(
        Category.SEMANTIC_FIELD_MISSING,
        exc.message,
        reference,
        cause=exc,
    )
