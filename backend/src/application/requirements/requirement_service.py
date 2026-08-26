"""Application service duy nhất cho module Requirement."""

from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.requirements.i_requirement_service import IRequirementService
from src.application.requirements.input import (
    AnalyzeRequirementClarificationInput,
    AnswerRequirementClarificationInput,
    ChooseRequirementContinuationInput,
    DeleteRequirementInput,
    GetRequirementClarificationInput,
    ListRequirementsInput,
    SendRequirementClarificationMessageInput,
)
from src.application.requirements.output import (
    RequirementClarificationStateOutput,
    RequirementOutput,
)
from src.application.requirements.requirement_clarification_coordinator import (
    RequirementClarificationCoordinator,
)
from src.application.requirements.requirement_continuation_coordinator import (
    RequirementContinuationCoordinator,
)
from src.domain.requirement.i_requirement_repository import IRequirementRepository
from typing_extensions import override


class RequirementService(IRequirementService):
    """Điều phối Requirement qua Domain repository và policy dự án."""

    def __init__(
        self,
        requirements: IRequirementRepository,
        access: ProjectAccessPolicy,
        clarification: RequirementClarificationCoordinator,
        continuation: RequirementContinuationCoordinator,
    ) -> None:
        self._requirements = requirements
        self._access = access
        self._clarification = clarification
        self._continuation = continuation

    @override
    async def list_requirements(
        self,
        data: ListRequirementsInput,
    ) -> list[RequirementOutput]:
        """Liệt kê yêu cầu nếu actor là thành viên dự án."""
        await self._access.require_member(data.project_id)
        requirements = await self._requirements.list_by_project(data.project_id)
        return [RequirementOutput.from_domain(item) for item in requirements]

    @override
    async def delete_requirement(self, data: DeleteRequirementInput) -> None:
        await self._clarification.delete_requirement(data)

    @override
    async def get_clarification(
        self, data: GetRequirementClarificationInput
    ) -> RequirementClarificationStateOutput:
        return await self._clarification.get_state(data)

    @override
    async def analyze_clarification(
        self, data: AnalyzeRequirementClarificationInput
    ) -> RequirementClarificationStateOutput:
        return await self._clarification.analyze(data)

    @override
    async def answer_clarification(
        self, data: AnswerRequirementClarificationInput
    ) -> RequirementClarificationStateOutput:
        return await self._clarification.answer(data)

    @override
    async def send_clarification_message(
        self, data: SendRequirementClarificationMessageInput
    ) -> RequirementClarificationStateOutput:
        return await self._clarification.message(data)

    @override
    async def choose_clarification_continuation(
        self, data: ChooseRequirementContinuationInput
    ) -> RequirementClarificationStateOutput:
        return await self._continuation.choose(data)
