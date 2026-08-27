"""Tạo feedback retry structured output không chứa raw response."""

from src.infrastructure.llm.structured_output_models import StructuredOutputIssue


def append_retry_feedback(
    user_prompt: str,
    issues: tuple[StructuredOutputIssue, ...],
) -> str:
    """Yêu cầu chỉ sửa input lỗi bằng feedback đã phân loại."""
    feedback = "\n".join(_render_issue(item) for item in issues)
    return f"""{user_prompt}

## Structured output correction
Correct only the failed requirements supplied above. Do not modify already-valid requirements.
Do not invent references, source tables, columns, or relationships. Use only canonical identifiers.
Validation feedback:
{feedback}"""


def _render_issue(issue: StructuredOutputIssue) -> str:
    reference = issue.reference or "GLOBAL"
    field = f" field={issue.field}" if issue.field else ""
    return f"- {reference}: {issue.category.value}{field}: {issue.message}"
