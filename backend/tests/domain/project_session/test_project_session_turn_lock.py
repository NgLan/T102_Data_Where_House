from datetime import timedelta
from uuid import uuid4

import pytest
from src.common.exceptions.business import BusinessException
from src.common.utils.datetime import utc_now
from src.domain.project_session.entities import ProjectSession
from src.domain.project_session.enums import (
    RequirementContinuationAction,
    RequirementContinuationState,
    SessionPurpose,
)


def test_active_turn_rejects_second_turn() -> None:
    session = ProjectSession(project_id=uuid4(), user_id=uuid4())
    session.acquire_turn(uuid4(), utc_now() - timedelta(minutes=15))

    with pytest.raises(BusinessException):
        session.acquire_turn(uuid4(), utc_now() - timedelta(minutes=15))


def test_stale_turn_can_be_replaced() -> None:
    session = ProjectSession(project_id=uuid4(), user_id=uuid4())
    stale_turn_id = uuid4()
    next_turn_id = uuid4()
    session.active_turn_id = stale_turn_id
    session.active_turn_started_at = utc_now() - timedelta(minutes=16)

    session.acquire_turn(next_turn_id, utc_now() - timedelta(minutes=15))

    assert session.active_turn_id == next_turn_id
    assert session.active_turn_started_at is not None


def test_pending_question_only_resumes_with_matching_id() -> None:
    session = ProjectSession(project_id=uuid4(), user_id=uuid4())
    turn_id = uuid4()
    question_id = uuid4()
    session.acquire_turn(turn_id, utc_now() - timedelta(minutes=15))
    session.wait_for_clarification(turn_id, question_id)

    with pytest.raises(BusinessException):
        session.resume_turn(uuid4(), turn_id, utc_now() - timedelta(minutes=15))

    session.resume_turn(question_id, turn_id, utc_now() - timedelta(minutes=15))
    assert session.pending_question_id is None
    assert session.active_turn_id == turn_id


def test_requirement_continuation_allows_editing_then_analysis() -> None:
    session = ProjectSession(
        project_id=uuid4(), user_id=uuid4(),
        purpose=SessionPurpose.REQUIREMENT_CLARIFICATION,
        base_requirement_revision=1,
    )
    session.await_continuation_decision()
    session.choose_continuation(RequirementContinuationAction.CONTINUE_EDITING)
    session.choose_continuation(RequirementContinuationAction.CONTINUE_ANALYSIS)

    assert session.requirement_continuation_state is RequirementContinuationState.CONTINUE_ANALYSIS


def test_requirement_continuation_cannot_reverse_analysis() -> None:
    session = ProjectSession(
        project_id=uuid4(), user_id=uuid4(),
        purpose=SessionPurpose.REQUIREMENT_CLARIFICATION,
        base_requirement_revision=1,
        requirement_continuation_state=RequirementContinuationState.CONTINUE_ANALYSIS,
    )

    with pytest.raises(BusinessException):
        session.choose_continuation(RequirementContinuationAction.CONTINUE_EDITING)
