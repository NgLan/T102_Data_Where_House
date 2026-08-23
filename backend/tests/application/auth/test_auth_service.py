"""Application tests cho auth không phụ thuộc HTTP hoặc PostgreSQL."""

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from src.application.auth.auth_service import AuthService
from src.application.auth.input import LoginInput, RegisterInput
from src.application.auth.token_models import IssuedToken, TokenClaims
from src.common.exceptions.business import BusinessException
from src.common.utils.datetime import utc_now
from src.domain.user.entities import User


def _service(user: User | None = None):
    users = MagicMock()
    users.get_by_username = AsyncMock(return_value=user)
    users.get_by_email = AsyncMock(return_value=None)
    users.get_by_id = AsyncMock(return_value=user)
    users.save = AsyncMock(side_effect=lambda item: item)
    revoked = MagicMock()
    revoked.exists = AsyncMock(return_value=False)
    revoked.save = AsyncMock()
    revoked.delete_expired = AsyncMock()
    passwords = MagicMock()
    passwords.hash.return_value = "hashed"
    passwords.verify.return_value = True
    expires = utc_now() + timedelta(minutes=30)
    claims = TokenClaims(user.id if user else uuid4(), "jti", utc_now(), expires)
    tokens = MagicMock()
    tokens.issue.return_value = IssuedToken("jwt", expires)
    tokens.decode.return_value = claims
    unit = MagicMock()
    unit.__aenter__ = AsyncMock(return_value=unit)
    unit.__aexit__ = AsyncMock(return_value=None)
    unit.commit = AsyncMock()
    return AuthService(users, revoked, passwords, tokens, unit), users, revoked


@pytest.mark.asyncio
async def test_register_hashes_password_and_issues_token() -> None:
    service, users, _ = _service()
    users.get_by_username.return_value = None
    result = await service.register(
        RegisterInput("new_user", "new@example.com", "securepass123", "New User")
    )

    assert result.access_token == "jwt"
    saved = users.save.await_args.args[0]
    assert saved.password_hash == "hashed"
    assert saved.is_active is True


@pytest.mark.asyncio
async def test_register_rejects_weak_password() -> None:
    service, _, _ = _service()
    with pytest.raises(BusinessException):
        await service.register(RegisterInput("user", "user@example.com", "short"))


@pytest.mark.asyncio
async def test_login_rejects_inactive_legacy_user() -> None:
    legacy = User(username="legacy", email="legacy@example.com", is_active=False)
    service, _, _ = _service(legacy)
    with pytest.raises(BusinessException):
        await service.login(LoginInput("legacy", "securepass123"))


@pytest.mark.asyncio
async def test_logout_persists_current_jti() -> None:
    user = User(
        username="active",
        email="active@example.com",
        password_hash="hashed",
        is_active=True,
    )
    service, _, revoked = _service(user)
    await service.logout("jwt")

    saved = revoked.save.await_args.args[0]
    assert saved.jti == "jti"
    assert saved.user_id == user.id
