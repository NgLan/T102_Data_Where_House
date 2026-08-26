"""State transition thuần cho Requirement continuation gate."""

from typing import Protocol

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.project_session.enums import (
    RequirementContinuationAction,
    RequirementContinuationState,
)


class RequirementContinuationTarget(Protocol):
    """Phần ProjectSession tối thiểu cần để mutate continuation state."""

    requirement_continuation_state: RequirementContinuationState

    def mark_updated(self) -> None: ...


def set_continuation_state(
    target: RequirementContinuationTarget, state: RequirementContinuationState
) -> None:
    """Gán state và cập nhật timestamp tại một điểm duy nhất."""
    target.requirement_continuation_state = state
    target.mark_updated()


def choose_requirement_continuation(
    target: RequirementContinuationTarget, action: RequirementContinuationAction
) -> None:
    """Áp dụng transition idempotent và cấm đảo ngược workflow đã resume."""
    desired = RequirementContinuationState(action.value)
    current = target.requirement_continuation_state
    if current is desired:
        return
    can_apply = current is RequirementContinuationState.AWAITING_DECISION or (
        current is RequirementContinuationState.CONTINUE_EDITING
        and desired is RequirementContinuationState.CONTINUE_ANALYSIS
    )
    if not can_apply:
        raise BusinessException(
            ErrorCode.REQUIREMENT_CONTINUATION_INVALID,
            "Requirement continuation transition không hợp lệ.",
        )
    set_continuation_state(target, desired)


class RequirementContinuationMixin:
    """Entity behavior nhỏ cho continuation gate, tách khỏi session lifecycle."""

    requirement_continuation_state: RequirementContinuationState

    def mark_updated(self) -> None: ...

    def await_continuation_decision(self) -> None:
        """Mở continuation gate sau một answer/follow-up turn đã READY."""
        set_continuation_state(self, RequirementContinuationState.AWAITING_DECISION)

    def clear_continuation_decision(self) -> None:
        """Bỏ continuation gate khi Agent còn cần clarification."""
        set_continuation_state(self, RequirementContinuationState.NOT_REQUIRED)

    def choose_continuation(self, action: RequirementContinuationAction) -> None:
        """Áp dụng transition idempotent và cấm đảo ngược workflow đã resume."""
        choose_requirement_continuation(self, action)
