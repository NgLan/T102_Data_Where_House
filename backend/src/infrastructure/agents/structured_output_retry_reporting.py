"""Safe diagnostics và public failure translation cho structured retry."""

from dataclasses import dataclass

from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.common.logging import get_logger
from src.infrastructure.llm.structured_output_models import (
    StructuredInvocationMetadata,
    StructuredOutputIssue,
)

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class StructuredIssueLogContext:
    """Thông tin invocation an toàn được phép ghi log."""

    operation: str
    attempt: int
    metadata: StructuredInvocationMetadata


def log_structured_issue(
    context: StructuredIssueLogContext,
    issue: StructuredOutputIssue,
) -> None:
    """Log metadata an toàn; logging filter bổ sung request/session context."""
    logger.warning(
        "RequirementAgent structured output requires correction.",
        extra={
            "event": "llm_structured_output_issue",
            "agent": "requirement_agent",
            "operation": context.operation,
            "attempt": context.attempt,
            "transport_ref": issue.reference,
            "failure_category": issue.category.value,
            "field": issue.field,
            "provider": context.metadata.provider,
            "model": context.metadata.model,
            "finish_reason": context.metadata.finish_reason,
        },
    )


def raise_structured_failure(issue: StructuredOutputIssue | None) -> None:
    """Dịch sang public error duy nhất sau khi bounded retry kết thúc."""
    cause = (
        issue.cause
        if issue and issue.cause
        else ValueError(issue.message if issue else "Structured output attempts exhausted.")
    )
    raise InfrastructureException(
        ErrorCode.LLM_STRUCTURED_OUTPUT_ERROR,
        "Structured output của RequirementAgent không hợp lệ sau khi retry.",
    ) from cause
