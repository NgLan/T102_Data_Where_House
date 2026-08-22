from uuid import uuid4

import pytest
from src.application.auth.output import CurrentActorOutput
from src.presentation.api.v1.auth import get_current_actor


@pytest.mark.asyncio
async def test_get_current_actor_returns_mvp_profile() -> None:
    actor = CurrentActorOutput(
        id=uuid4(), username="mvp-user", email="mvp@example.com",
    )

    response = await get_current_actor(actor)

    assert response.id == actor.id
    assert response.username == "mvp-user"
    assert response.email == "mvp@example.com"
