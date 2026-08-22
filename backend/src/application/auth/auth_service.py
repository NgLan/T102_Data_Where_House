"""Application service duy nhất của module Authentication."""

from src.application.auth.i_auth_service import IAuthService
from src.application.auth.input import ResolveCurrentActorInput
from src.application.auth.output import CurrentActorOutput
from src.application.common.unit_of_work import IUnitOfWork
from src.domain.user.entities import User
from src.domain.user.i_user_repository import IUserRepository
from typing_extensions import override


class AuthService(IAuthService):
    """Resolve actor MVP qua Domain repository và transaction abstraction."""

    def __init__(self, users: IUserRepository, unit_of_work: IUnitOfWork) -> None:
        self._users = users
        self._unit_of_work = unit_of_work

    @override
    async def resolve_current_actor(
        self,
        data: ResolveCurrentActorInput,
    ) -> CurrentActorOutput:
        """Lấy actor hiện hữu hoặc provision danh tính MVP.

        Raises:
            BusinessException: Khi thông tin user không thỏa Domain invariant.
            InfrastructureException: Khi persistence thất bại.
        """
        async with self._unit_of_work:
            user = await self._users.get_by_id(data.user_id)
            if user is not None:
                return CurrentActorOutput.from_domain(user)
            user = await self._users.save(
                User(id=data.user_id, username=data.username, email=data.email)
            )
            await self._unit_of_work.commit()
        return CurrentActorOutput.from_domain(user)
