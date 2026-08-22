"""Interface duy nhất của module Authentication."""

from abc import ABC, abstractmethod

from src.application.auth.input import ResolveCurrentActorInput
from src.application.auth.output import CurrentActorOutput


class IAuthService(ABC):
    """Hợp đồng application cho việc resolve actor hiện tại."""

    @abstractmethod
    async def resolve_current_actor(
        self,
        data: ResolveCurrentActorInput,
    ) -> CurrentActorOutput:
        """Lấy hoặc provision actor hiện tại.

        Args:
            data: Danh tính cần resolve.
        Returns:
            Actor được dùng tại application boundary.
        Raises:
            BusinessException: Khi danh tính vi phạm Domain invariant.
            InfrastructureException: Khi persistence thất bại.
        """
        raise NotImplementedError
