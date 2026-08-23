"""Public input models của application service Authentication."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RegisterInput:
    username: str
    email: str
    password: str
    full_name: str | None = None


@dataclass(frozen=True, slots=True)
class LoginInput:
    identifier: str
    password: str


__all__ = ["LoginInput", "RegisterInput"]
