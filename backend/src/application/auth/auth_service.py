"""Application service duy nhất của module Authentication."""

import re
from typing import NoReturn

from src.application.auth.i_auth_service import IAuthService, IPasswordHasher, ITokenCodec
from src.application.auth.input import LoginInput, RegisterInput
from src.application.auth.output import AuthSessionOutput, CurrentActorOutput
from src.application.auth.token_models import IssuedToken
from src.application.common.unit_of_work import IUnitOfWork
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.utils.datetime import utc_now
from src.domain.user.entities import User
from src.domain.user.i_revoked_token_repository import IRevokedTokenRepository
from src.domain.user.i_user_repository import IUserRepository
from src.domain.user.revoked_token import RevokedToken
from typing_extensions import override

MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_BYTES = 72


class AuthService(IAuthService):
    """Điều phối credential, JWT và revocation qua các outbound port."""

    def __init__(
        self,
        users: IUserRepository,
        revoked_tokens: IRevokedTokenRepository,
        passwords: IPasswordHasher,
        tokens: ITokenCodec,
        unit_of_work: IUnitOfWork,
    ) -> None:
        self._users = users
        self._revoked_tokens = revoked_tokens
        self._passwords = passwords
        self._tokens = tokens
        self._unit_of_work = unit_of_work

    @override
    async def register(self, data: RegisterInput) -> AuthSessionOutput:
        _validate_password(data.password)
        async with self._unit_of_work:
            if await self._users.get_by_username(data.username):
                _raise(ErrorCode.USERNAME_ALREADY_EXISTS, "Tên đăng nhập đã tồn tại.")
            if await self._users.get_by_email(data.email):
                _raise(ErrorCode.EMAIL_ALREADY_EXISTS, "Email đã tồn tại.")
            user = await self._users.save(
                User(
                    username=data.username,
                    email=data.email,
                    password_hash=self._passwords.hash(data.password),
                    full_name=data.full_name,
                    is_active=True,
                )
            )
            await self._unit_of_work.commit()
        return _session(user, self._tokens.issue(user.id))

    @override
    async def login(self, data: LoginInput) -> AuthSessionOutput:
        user = await self._find_user(data.identifier)
        valid = bool(
            user
            and user.is_active
            and user.password_hash
            and self._passwords.verify(data.password, user.password_hash)
        )
        if not valid or user is None:
            _raise(ErrorCode.INVALID_CREDENTIALS, "Thông tin đăng nhập không hợp lệ.")
        return _session(user, self._tokens.issue(user.id))

    @override
    async def authenticate(self, token: str) -> CurrentActorOutput:
        claims = self._tokens.decode(token)
        if await self._revoked_tokens.exists(claims.jti):
            _raise(ErrorCode.TOKEN_INVALID, "Token đã bị thu hồi.")
        user = await self._users.get_by_id(claims.user_id)
        if user is None or not user.is_active or user.password_hash is None:
            _raise(ErrorCode.AUTHENTICATION_REQUIRED, "Vui lòng đăng nhập để tiếp tục.")
        return CurrentActorOutput.from_domain(user)

    @override
    async def logout(self, token: str) -> None:
        claims = self._tokens.decode(token)
        async with self._unit_of_work:
            await self._revoked_tokens.delete_expired(utc_now())
            if not await self._revoked_tokens.exists(claims.jti):
                await self._revoked_tokens.save(
                    RevokedToken(
                        jti=claims.jti,
                        user_id=claims.user_id,
                        expires_at=claims.expires_at,
                    )
                )
            await self._unit_of_work.commit()

    async def _find_user(self, identifier: str) -> User | None:
        normalized = identifier.strip()
        if "@" in normalized:
            return await self._users.get_by_email(normalized)
        return await self._users.get_by_username(normalized)


def _validate_password(password: str) -> None:
    byte_length = len(password.encode("utf-8"))
    if len(password) < MIN_PASSWORD_LENGTH or byte_length > MAX_PASSWORD_BYTES:
        _raise(ErrorCode.WEAK_PASSWORD, "Mật khẩu phải dài 12–72 byte.")
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        _raise(ErrorCode.WEAK_PASSWORD, "Mật khẩu phải chứa ít nhất một chữ và một số.")


def _session(user: User, token: IssuedToken) -> AuthSessionOutput:
    return AuthSessionOutput(token.value, token.expires_at, CurrentActorOutput.from_domain(user))


def _raise(code: ErrorCode, message: str) -> NoReturn:
    raise BusinessException(code, message)
