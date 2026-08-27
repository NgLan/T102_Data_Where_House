"""Whole-call bounded retry cho Requirement clarification output."""

from pydantic import ValidationError
from src.application.requirements.input import ClarifyRequirementsInput
from src.infrastructure.agents.prompts.requirement import (
    REQUIREMENT_CLARIFICATION_SYSTEM_PROMPT,
    REQUIREMENT_CLARIFICATION_USER_PROMPT,
)
from src.infrastructure.agents.requirement_context_renderer import render_requirement_clarification
from src.infrastructure.agents.structured_output_retry_reporting import (
    StructuredIssueLogContext,
    log_structured_issue,
    raise_structured_failure,
)
from src.infrastructure.agents.structured_retry_prompt import append_retry_feedback
from src.infrastructure.agents.transport_references import TransportReferenceMap
from src.infrastructure.llm.agent_structured_outputs import (
    RequirementClarificationResult,
)
from src.infrastructure.llm.structured_llm_invoker import StructuredLlmInvoker
from src.infrastructure.llm.structured_output_models import (
    StructuredOutputFailureCategory as Category,
)
from src.infrastructure.llm.structured_output_models import StructuredOutputIssue


class ClarificationOutputRetry:
    """Retry toàn result vì requirement set và readiness phụ thuộc lẫn nhau."""

    def __init__(self, invoker: StructuredLlmInvoker, max_attempts: int) -> None:
        self._invoker = invoker
        self._max_attempts = max_attempts

    async def invoke(
        self,
        data: ClarifyRequirementsInput,
        references: TransportReferenceMap,
    ) -> RequirementClarificationResult:
        """Trả complete clarification result hoặc lỗi public sau max attempts."""
        sections = render_requirement_clarification(data, references)
        base_prompt = REQUIREMENT_CLARIFICATION_USER_PROMPT.format(**sections)
        issues: tuple[StructuredOutputIssue, ...] = ()
        last_issue: StructuredOutputIssue | None = None
        for attempt in range(1, self._max_attempts + 1):
            prompt = append_retry_feedback(base_prompt, issues) if issues else base_prompt
            response = await self._invoker.invoke_payload(
                REQUIREMENT_CLARIFICATION_SYSTEM_PROMPT,
                prompt,
                RequirementClarificationResult,
            )
            result, issues = self._validate(response.payload, response.issue, references)
            context = StructuredIssueLogContext("clarify_requirements", attempt, response.metadata)
            for issue in issues:
                log_structured_issue(context, issue)
            if result is not None:
                return result
            last_issue = issues[-1] if issues else response.issue
        raise_structured_failure(last_issue)

    @staticmethod
    def _validate(
        payload: dict[str, object] | None,
        decode_issue: StructuredOutputIssue | None,
        references: TransportReferenceMap,
    ) -> tuple[RequirementClarificationResult | None, tuple[StructuredOutputIssue, ...]]:
        if payload is None:
            return None, (decode_issue,) if decode_issue else ()
        try:
            result = RequirementClarificationResult.model_validate(payload)
        except ValidationError as exc:
            error = exc.errors(include_url=False)[0]
            field = ".".join(str(value) for value in error.get("loc", ())) or None
            issue = StructuredOutputIssue(
                Category.PYDANTIC_SCHEMA_ERROR,
                str(error["msg"]),
                field=field,
                cause=exc,
            )
            return None, (issue,)
        issues = ClarificationOutputRetry._reference_issues(result, references)
        return (None, issues) if issues else (result, ())

    @staticmethod
    def _reference_issues(
        result: RequirementClarificationResult,
        references: TransportReferenceMap,
    ) -> tuple[StructuredOutputIssue, ...]:
        returned = [item.existing_requirement_ref for item in result.requirements if item.existing_requirement_ref]
        duplicate = {value for value in returned if returned.count(value) > 1}
        unknown = set(returned) - set(references.references)
        issues = [
            StructuredOutputIssue(Category.REQUIREMENT_REF_DUPLICATED, "Reference is duplicated.", value)
            for value in sorted(duplicate)
        ]
        issues += [
            StructuredOutputIssue(Category.REQUIREMENT_REF_UNKNOWN, "Reference is not canonical.", value)
            for value in sorted(unknown)
        ]
        return tuple(issues)
