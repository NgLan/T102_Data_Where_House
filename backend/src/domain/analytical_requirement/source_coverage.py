"""Assessment và resolution state của Source Coverage."""

from dataclasses import dataclass, field, replace

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.analytical_requirement.enums import (
    SourceConfirmationQuestionType,
    SourceConfirmationStatus,
    SourceCoverageStatus,
)
from src.domain.analytical_requirement.source_confirmation_rules import (
    validate_question_candidates,
)
from src.domain.analytical_requirement.source_coverage_candidate import (
    SourceCoverageCandidate,
)
from src.domain.shared.enum_rules import normalize_str_enum
from src.domain.shared.types import EntityID
from src.domain.shared.value_object import BaseValueObject


@dataclass(frozen=True)
class SourceCoverageAssessment(BaseValueObject):
    """Kết luận coverage cho đúng một business concept cần thiết."""

    id: EntityID
    batch_id: EntityID
    evaluated_source_revision: int
    status: SourceCoverageStatus
    required_concept_key: str
    title: str
    explanation: str
    question: str | None = None
    question_type: SourceConfirmationQuestionType | None = None
    confirmation_status: SourceConfirmationStatus | None = None
    selected_candidate_id: EntityID | None = None
    resolution_revision: int = 0
    applied_source_revision: int | None = None
    candidates: tuple[SourceCoverageCandidate, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        status = normalize_str_enum(self.status, SourceCoverageStatus, ErrorCode.VALIDATION_ERROR)
        key = self.required_concept_key.strip()
        title, explanation = self.title.strip(), self.explanation.strip()
        question = self.question.strip() if self.question else None
        question_type = self._normalize_question_type(status)
        candidates = tuple(self.candidates)
        if not key or not title or not explanation:
            raise BusinessException(
                ErrorCode.VALIDATION_ERROR,
                "Source coverage phải có semantic key và nội dung hiển thị.",
            )
        confirmation = self._normalize_confirmation(status)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "required_concept_key", key)
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "explanation", explanation)
        object.__setattr__(self, "question", question)
        object.__setattr__(self, "question_type", question_type)
        object.__setattr__(self, "confirmation_status", confirmation)
        object.__setattr__(self, "candidates", candidates)
        self._validate_shape(status, confirmation, question_type)

    def _normalize_question_type(self, status: SourceCoverageStatus) -> SourceConfirmationQuestionType | None:
        if status is not SourceCoverageStatus.NEEDS_SOURCE_CONFIRMATION:
            if self.question_type is not None:
                raise BusinessException(
                    ErrorCode.VALIDATION_ERROR,
                    "Chỉ Source Confirmation được có question type.",
                )
            return None
        if self.question_type is None:
            raise BusinessException(ErrorCode.VALIDATION_ERROR, "Confirmation phải có question type.")
        return normalize_str_enum(
            self.question_type,
            SourceConfirmationQuestionType,
            ErrorCode.VALIDATION_ERROR,
        )

    def _normalize_confirmation(self, status: SourceCoverageStatus) -> SourceConfirmationStatus | None:
        if status is not SourceCoverageStatus.NEEDS_SOURCE_CONFIRMATION:
            return None
        return normalize_str_enum(
            self.confirmation_status or SourceConfirmationStatus.PENDING,
            SourceConfirmationStatus,
            ErrorCode.VALIDATION_ERROR,
        )

    def _validate_shape(
        self,
        status: SourceCoverageStatus,
        confirmation: SourceConfirmationStatus | None,
        question_type: SourceConfirmationQuestionType | None,
    ) -> None:
        needs_confirmation = status is SourceCoverageStatus.NEEDS_SOURCE_CONFIRMATION
        if needs_confirmation != bool(self.candidates and self.question):
            raise BusinessException(ErrorCode.VALIDATION_ERROR, "Confirmation shape không hợp lệ.")
        if not needs_confirmation and (self.question or self.candidates):
            raise BusinessException(
                ErrorCode.VALIDATION_ERROR,
                "Chỉ Source Confirmation được có question contract.",
            )
        if status is SourceCoverageStatus.MISSING_SOURCE and self.candidates:
            raise BusinessException(ErrorCode.VALIDATION_ERROR, "Missing source không có candidate.")
        if needs_confirmation and question_type is not None:
            validate_question_candidates(question_type, self.candidates)
        selected = self.selected_candidate_id
        if confirmation is SourceConfirmationStatus.CONFIRMED:
            if selected not in {item.id for item in self.candidates}:
                raise BusinessException(ErrorCode.VALIDATION_ERROR, "Candidate đã chọn không hợp lệ.")
        elif selected is not None:
            raise BusinessException(ErrorCode.VALIDATION_ERROR, "Chỉ CONFIRMED được có candidate.")

    def with_resolution(
        self, status: SourceConfirmationStatus, candidate_id: EntityID | None
    ) -> "SourceCoverageAssessment":
        """Tạo snapshot item mới và tăng optimistic resolution revision."""
        return replace(
            self,
            confirmation_status=status,
            selected_candidate_id=candidate_id,
            resolution_revision=self.resolution_revision + 1,
        )

    def with_applied_source_revision(self, source_revision: int) -> "SourceCoverageAssessment":
        """Đánh dấu decision của batch đã được materialize vào SchemaMetadata."""
        return replace(self, applied_source_revision=source_revision)
