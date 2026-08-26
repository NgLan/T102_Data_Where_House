"""Atomically apply RequirementAgent result khi base revision còn hiện hành."""

from src.application.requirements.output import RequirementClarificationResult
from src.application.requirements.requirement_clarification_dependencies import (
    RequirementClarificationDependencies,
)
from src.application.requirements.requirement_clarification_event_writer import (
    RequirementClarificationEventWriter,
    RequirementTurnCompletionInput,
)
from src.application.requirements.requirement_clarification_turn_start import (
    RequirementTurnStart,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.project_session.entities import ProjectSession, SessionEvent


class RequirementClarificationTurnCompletion:
    """Persist technical/public events và canonical structured Requirements."""

    def __init__(self, dependencies: RequirementClarificationDependencies) -> None:
        self._dependencies = dependencies
        self._writer = RequirementClarificationEventWriter(dependencies)

    async def complete(
        self,
        start: RequirementTurnStart,
        result: RequirementClarificationResult,
    ) -> None:
        is_stale = await self._complete_locked(start, result)
        if is_stale:
            raise BusinessException(
                ErrorCode.ANALYSIS_INPUT_CHANGED,
                "Requirement đã thay đổi trong khi Agent đang xử lý.",
            )

    async def _complete_locked(
        self,
        start: RequirementTurnStart,
        result: RequirementClarificationResult,
    ) -> bool:
        dependencies = self._dependencies
        is_stale = False
        async with dependencies.unit_of_work:
            project = await dependencies.access.require_owner_for_update(start.session.project_id)
            current = await dependencies.sessions.get_by_id_for_update(start.session.id)
            if current is None:
                raise BusinessException(ErrorCode.SESSION_NOT_FOUND, "Session không tồn tại.")
            if _is_stale(project.requirement_revision, current, start.call):
                await self._writer.archive_stale(current, start.call)
                is_stale = True
            else:
                await self._writer.apply(
                    RequirementTurnCompletionInput(
                        current,
                        start.call,
                        result,
                        project,
                        start.requires_continuation_decision,
                    )
                )
            await dependencies.unit_of_work.commit()
        return is_stale

    async def fail(self, session: ProjectSession, call: SessionEvent) -> None:
        """Giải phóng đúng turn và lưu technical failure, không tạo public message."""
        dependencies = self._dependencies
        async with dependencies.unit_of_work:
            current = await dependencies.sessions.get_by_id_for_update(session.id)
            if current is None:
                return
            await self._writer.persist_failure(current, call)
            await dependencies.unit_of_work.commit()


def _is_stale(
    requirement_revision: int,
    session: ProjectSession,
    call: SessionEvent,
) -> bool:
    return (
        session.base_requirement_revision != requirement_revision
        or session.active_turn_id != call.turn_id
    )
