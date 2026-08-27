"""Ordered provider routing policy độc lập credential selection."""

from dataclasses import dataclass
from typing import Generic, TypeVar

Route = TypeVar("Route")


@dataclass(frozen=True, slots=True)
class ProviderRoutingPolicy(Generic[Route]):
    """Giữ ordered candidates đã resolve từ configuration."""

    candidates: tuple[Route, ...]

    def ordered(self) -> tuple[Route, ...]:
        """Trả candidates đúng thứ tự, không tự suy đoán provider."""
        return self.candidates
