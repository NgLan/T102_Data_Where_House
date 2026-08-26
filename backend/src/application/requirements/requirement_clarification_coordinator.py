"""Orchestrate Requirement clarification turns ngoài database transaction."""

from src.application.project_sessions.clarification_context import (
    create_clarification_memory_input,
)
from src.application.project_sessions.conversation_context import (
    ConversationInputKind,
    ConversationMemory,
)
from src.application.project_sessions.conversation_context_policy import (
    ConversationMemoryInput,
)
from src.application.requirements.input import (
    AnalyzeRequirementClarificationInput,
    AnswerRequirementClarificationInput,
    ClarifyRequirementsInput,
    DeleteRequirementInput,
    GetRequirementClarificationInput,
    RequirementDocumentContext,
    SendRequirementClarificationMessageInput,
)
from src.application.requirements.output import RequirementClarificationStateOutput
from src.application.requirements.requirement_clarification_answer_turn import (
    RequirementClarificationAnswerTurn,
)
from src.application.requirements.requirement_clarification_dependencies import (
    RequirementClarificationDependencies,
)
from src.application.requirements.requirement_clarification_turn_completion import (
    RequirementClarificationTurnCompletion,
)
from src.application.requirements.requirement_clarification_turn_start import (
    RequirementClarificationTurnStarter,
    RequirementTurnStart,
)
from src.application.requirements.requirement_mapping import to_requirement_context
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode


class RequirementClarificationCoordinator:
    """Dùng session audit/context chung nhưng chỉ gọi RequirementAgent."""

    def __init__(self, dependencies: RequirementClarificationDependencies) -> None:
        self._dependencies = dependencies
        self._starter = RequirementClarificationTurnStarter(dependencies)
        self._answer_turn = RequirementClarificationAnswerTurn(dependencies)
        self._completion = RequirementClarificationTurnCompletion(dependencies)

    async def get_state(
        self, data: GetRequirementClarificationInput
    ) -> RequirementClarificationStateOutput:
        project = (await self._dependencies.access.require_member(data.project_id)).project
        return await self._dependencies.state.read(project)

    async def analyze(
        self, data: AnalyzeRequirementClarificationInput
    ) -> RequirementClarificationStateOutput:
        start = await self._starter.analyze(data)
        await self._execute(start)
        return await self.get_state(GetRequirementClarificationInput(data.project_id))

    async def answer(
        self, data: AnswerRequirementClarificationInput
    ) -> RequirementClarificationStateOutput:
        start = await self._answer_turn.start(data)
        await self._execute(start)
        return await self.get_state(GetRequirementClarificationInput(data.project_id))

    async def message(
        self, data: SendRequirementClarificationMessageInput
    ) -> RequirementClarificationStateOutput:
        """Chạy follow-up turn ngay cả khi structured output đã READY."""
        start = await self._starter.message(data)
        await self._execute(start)
        return await self.get_state(GetRequirementClarificationInput(data.project_id))

    async def delete_requirement(self, data: DeleteRequirementInput) -> None:
        """Xóa structured item và làm analytical output outdated atomically."""
        dependencies = self._dependencies
        async with dependencies.unit_of_work:
            project = await dependencies.access.require_owner_for_update(data.project_id)
            requirement = await dependencies.requirements.get_by_id(data.requirement_id)
            if requirement is None or requirement.project_id != project.id:
                raise BusinessException(ErrorCode.REQUIREMENT_NOT_FOUND, "Requirement không tồn tại.")
            await dependencies.requirements.delete(requirement.id)
            project.mark_analytical_requirements_derived(is_outdated=True)
            await dependencies.projects.save(project)
            await dependencies.unit_of_work.commit()

    async def _execute(self, start: RequirementTurnStart) -> None:
        try:
            agent_input = await self._agent_input(start)
            result = await self._dependencies.agent.clarify_requirements(agent_input)
        except Exception:
            await self._completion.fail(start.session, start.call)
            raise
        await self._completion.complete(start, result)
        await self._dependencies.context.compact_after_completion(
            start.session.id, start.session.project_id
        )

    async def _agent_input(self, start: RequirementTurnStart) -> ClarifyRequirementsInput:
        dependencies = self._dependencies
        project = await dependencies.projects.get_by_id(start.session.project_id)
        if project is None:
            raise BusinessException(ErrorCode.PROJECT_NOT_FOUND, "Project không tồn tại.")
        documents = await dependencies.requirement_files.list_by_project(project.id)
        requirements = await dependencies.requirements.list_by_project(project.id)
        memory = await self._memory(start)
        return ClarifyRequirementsInput(
            project.requirement or "",
            tuple(
                RequirementDocumentContext(item.name, item.extracted_text)
                for item in documents
            ),
            tuple(to_requirement_context(item) for item in requirements),
            memory,
        )

    async def _memory(self, start: RequirementTurnStart) -> ConversationMemory:
        if start.question and start.current_input:
            memory_input, _ = create_clarification_memory_input(
                start.session, start.question, start.current_input
            )
        else:
            memory_input = ConversationMemoryInput(
                start.session.id,
                start.session.project_id,
                start.current_input or "Analyze the saved requirement context.",
                ConversationInputKind.USER_MESSAGE,
            )
        return await self._dependencies.context.build_memory(memory_input)
