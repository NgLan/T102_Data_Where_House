from datetime import timedelta
from uuid import uuid4

import pytest
from src.common.exceptions.business import BusinessException
from src.common.utils.datetime import utc_now
from src.domain.project_session.entities import ProjectSession


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
