"""Invariant cấu trúc cho từng loại Source Confirmation."""

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.analytical_requirement.enums import (
    SourceCandidateKind,
    SourceConfirmationQuestionType,
)
from src.domain.analytical_requirement.source_coverage_candidate import (
    SourceCoverageCandidate,
)


def validate_question_candidates(
    question_type: SourceConfirmationQuestionType,
    candidates: tuple[SourceCoverageCandidate, ...],
) -> None:
    """Xác minh candidate mappings trả lời đúng loại câu hỏi."""
    if question_type is SourceConfirmationQuestionType.FIELD_SET_CONFIRMATION:
        valid = len(candidates) == 1 and _is_field_set(candidates[0])
    elif question_type is SourceConfirmationQuestionType.RELATIONSHIP_CONFIRMATION:
        valid = len(candidates) == 1 and _is_relationship_set(candidates[0])
    elif question_type is SourceConfirmationQuestionType.SINGLE_CANDIDATE_CONFIRMATION:
        valid = len(candidates) == 1 and _is_single_column(candidates[0])
    else:
        valid = len(candidates) >= 2 and all(_is_single_column(item) for item in candidates)
    if not valid:
        raise BusinessException(
            ErrorCode.VALIDATION_ERROR,
            "Candidate mappings không khớp loại câu hỏi Source Confirmation.",
        )


def _is_single_column(candidate: SourceCoverageCandidate) -> bool:
    if len(candidate.references) != 1:
        return False
    reference = candidate.references[0]
    return reference.kind is SourceCandidateKind.COLUMN and reference.role_key is None


def _is_field_set(candidate: SourceCoverageCandidate) -> bool:
    references = candidate.references
    roles = [item.role_key for item in references]
    return (
        len(references) >= 2
        and all(item.kind is SourceCandidateKind.COLUMN and item.role_key for item in references)
        and len(roles) == len(set(roles))
    )


def _is_relationship_set(candidate: SourceCoverageCandidate) -> bool:
    return all(item.kind is SourceCandidateKind.RELATIONSHIP and item.role_key is None for item in candidate.references)
