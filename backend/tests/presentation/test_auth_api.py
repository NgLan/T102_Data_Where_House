from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import Response
from src.application.auth.output import AuthSessionOutput, CurrentActorOutput
from src.presentation.api.v1.auth import _set_auth_cookie, get_current_actor


@pytest.mark.asyncio
async def test_get_current_actor_returns_mvp_profile() -> None:
    actor = CurrentActorOutput(
        id=uuid4(),
        username="user",
        email="user@example.com",
        full_name="Test User",
        is_active=True,
        created_at=datetime.now(UTC),
    )

    response = await get_current_actor(actor)

    assert response.id == actor.id
    assert response.username == "user"
    assert response.email == "user@example.com"


def test_auth_cookie_is_http_only_none_secure_and_api_scoped_in_prod(monkeypatch) -> None:
    actor = CurrentActorOutput(
        id=uuid4(),
        username="user",
        email="user@example.com",
        full_name=None,
        is_active=True,
        created_at=datetime.now(UTC),
    )
    session = AuthSessionOutput(
        "signed-token",
        datetime.now(UTC) + timedelta(minutes=30),
        actor,
    )
    monkeypatch.setattr(
        "src.presentation.api.v1.auth.get_settings",
        lambda: SimpleNamespace(app_env="production"),
    )
    response = Response()

    _set_auth_cookie(response, session)

    cookie = response.headers["set-cookie"]
    assert "p102_access_token=signed-token" in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=none" in cookie
    assert "Secure" in cookie
    assert "Path=/api/v1" in cookie


def test_auth_cookie_is_lax_in_development(monkeypatch) -> None:
    actor = CurrentActorOutput(
        id=uuid4(),
        username="user",
        email="user@example.com",
        full_name=None,
        is_active=True,
        created_at=datetime.now(UTC),
    )
    session = AuthSessionOutput(
        "signed-token",
        datetime.now(UTC) + timedelta(minutes=30),
        actor,
    )
    monkeypatch.setattr(
        "src.presentation.api.v1.auth.get_settings",
        lambda: SimpleNamespace(app_env="development"),
    )
    response = Response()

    _set_auth_cookie(response, session)

    cookie = response.headers["set-cookie"]
    assert "SameSite=lax" in cookie
