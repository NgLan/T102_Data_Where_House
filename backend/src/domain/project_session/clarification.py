"""Value object cho vòng đời clarification của phiên Agent."""

from dataclasses import dataclass

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_model.enums import DataModelTargetKind
from src.domain.project_session.enums import ClarificationAnswerKind, SessionQuestionKind
from src.domain.sandbox.enums import SandboxDbType, SandboxEndpointRisk
from src.domain.shared.enum_rules import normalize_str_enum
from src.domain.shared.types import EntityID
from src.domain.shared.value_object import BaseValueObject


@dataclass(frozen=True)
class ClarificationQuestionMetadata(BaseValueObject):
    """Các lựa chọn có căn cứ đi kèm một câu hỏi làm rõ."""

    options: tuple[str, ...]
    allow_custom_answer: bool = True
    reason: str | None = None
    original_intent: str | None = None
    missing_information: str | None = None
    question_kind: SessionQuestionKind = SessionQuestionKind.CLARIFICATION
    tool_name: str | None = None
    target_kind: DataModelTargetKind | None = None
    proposal_change_id: EntityID | None = None
    db_type: SandboxDbType | None = None
    reset_schema: bool | None = None
    expected_revision: int | None = None
    endpoint_risk: SandboxEndpointRisk | None = None
    schema_name: str | None = None

    def __post_init__(self) -> None:
        normalized = tuple(option.strip() for option in self.options if option.strip())
        if not 1 <= len(normalized) <= 4 or len(set(normalized)) != len(normalized):
            _raise_invalid("Clarification phải có từ một đến bốn lựa chọn duy nhất.")
        if (
            self.question_kind is SessionQuestionKind.CLARIFICATION
            and not self.allow_custom_answer
        ):
            _raise_invalid("Clarification phải cho phép người dùng nhập câu trả lời khác.")
        object.__setattr__(self, "options", normalized)
        object.__setattr__(self, "reason", self.reason.strip() if self.reason else None)
        object.__setattr__(self, "original_intent", self.original_intent.strip() if self.original_intent else None)
        object.__setattr__(
            self,
            "missing_information",
            self.missing_information.strip() if self.missing_information else None,
        )


@dataclass(frozen=True)
class ClarificationAnswerMetadata(BaseValueObject):
    """Liên kết một answer chính xác với question đã phát sinh nó."""

    question_id: EntityID
    kind: ClarificationAnswerKind
    option_index: int | None = None

    def __post_init__(self) -> None:
        kind = normalize_str_enum(self.kind, ClarificationAnswerKind, ErrorCode.VALIDATION_ERROR)
        object.__setattr__(self, "kind", kind)
        if kind is ClarificationAnswerKind.OPTION and self.option_index is None:
            _raise_invalid("Câu trả lời theo lựa chọn phải có option_index.")
        if kind is ClarificationAnswerKind.CUSTOM and self.option_index is not None:
            _raise_invalid("Câu trả lời tùy chỉnh không được có option_index.")


def _raise_invalid(message: str) -> None:
    raise BusinessException(ErrorCode.VALIDATION_ERROR, message)
