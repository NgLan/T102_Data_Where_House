"""Định nghĩa các kiểu dữ liệu chung (domain types) cho tầng Domain."""

from typing import TypeAlias
from uuid import UUID

EntityID = UUID
JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
