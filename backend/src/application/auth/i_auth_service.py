"""Interface duy nhất của module Authentication."""

from abc import ABC, abstractmethod
from typing import Protocol

from src.application.auth.input import LoginInput, RegisterInput
from src.application.auth.output import AuthSessionOutput, CurrentActorOutput
from src.application.auth.token_models import IssuedToken, TokenClaims
from src.domain.shared.types import EntityID


class IPasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...

    def verify(self, password: str, password_hash: str) -> bool: ...


class ITokenCodec(Protocol):
    def issue(self, user_id: EntityID) -> IssuedToken: ...

    def decode(self, token: str) -> TokenClaims: ...


class IAuthService(ABC):
    """Hợp đồng application cho đăng ký, đăng nhập và thu hồi JWT."""

    @abstractmethod
    async def register(self, data: RegisterInput) -> AuthSessionOutput: ...

    @abstractmethod
    async def login(self, data: LoginInput) -> AuthSessionOutput: ...

    @abstractmethod
    async def authenticate(self, token: str) -> CurrentActorOutput: ...

    @abstractmethod
    async def logout(self, token: str) -> None: ...
