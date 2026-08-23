"""Security adapter tests for password cost and strict JWT validation."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest
from src.common.exceptions.business import BusinessException
from src.infrastructure.security.jwt_token_codec import ALGORITHM, JwtTokenCodec
from src.infrastructure.security.password_hasher import BcryptPasswordHasher

ISSUER_SECRET = "issuer-secret-that-is-at-least-32-bytes"
VERIFIER_SECRET = "verifier-secret-that-is-at-least-32-bytes"
TEST_SECRET = "test-secret-that-is-at-least-32-bytes"


def test_bcrypt_hash_uses_cost_12_and_verifies() -> None:
    hasher = BcryptPasswordHasher()
    encoded = hasher.hash("secure-password-123")

    assert encoded.split("$")[2] == "12"
    assert hasher.verify("secure-password-123", encoded) is True
    assert hasher.verify("wrong-password", encoded) is False


def test_jwt_round_trip_contains_subject_and_unique_jti() -> None:
    codec = JwtTokenCodec(TEST_SECRET, 30)
    user_id = uuid4()

    first = codec.decode(codec.issue(user_id).value)
    second = codec.decode(codec.issue(user_id).value)

    assert first.user_id == user_id
    assert first.jti != second.jti
    assert first.expires_at > first.issued_at


@pytest.mark.parametrize("secret", ["wrong-secret", ""])
def test_jwt_rejects_wrong_signature_or_missing_token(secret: str) -> None:
    token = JwtTokenCodec(ISSUER_SECRET, 30).issue(uuid4()).value if secret else ""
    with pytest.raises(BusinessException):
        JwtTokenCodec(VERIFIER_SECRET, 30).decode(token)


def test_jwt_rejects_expired_token() -> None:
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "jti": str(uuid4()),
            "iat": now - timedelta(hours=2),
            "exp": now - timedelta(hours=1),
            "type": "access",
        },
        TEST_SECRET,
        algorithm=ALGORITHM,
    )
    with pytest.raises(BusinessException):
        JwtTokenCodec(TEST_SECRET, 30).decode(token)
