"""Persist lựa chọn continuation của Requirement workflow."""

from src.application.requirements.input import ChooseRequirementContinuationInput
from src.application.requirements.output import RequirementClarificationStateOutput
from src.application.requirements.requirement_clarification_dependencies import (
    RequirementClarificationDependencies,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.project.entities import Project
from src.domain.project_session.entities import ProjectSession
from src.domain.project_session.enums import (
    SessionPurpose,
    SessionStatus,
)


class RequirementContinuationCoordinator:
    """Validate và lưu continuation action dưới cùng Project/session lock."""

    def __init__(self, dependencies: RequirementClarificationDependencies) -> None:
        self._dependencies = dependencies

    async def choose(
        self, data: ChooseRequirementContinuationInput
    ) -> RequirementClarificationStateOutput:
        dependencies = self._dependencies
        async with dependencies.unit_of_work:
            project = await dependencies.access.require_owner_for_update(data.project_id)
            session = await dependencies.sessions.get_by_id_for_update(data.session_id)
            if session is None:
                raise BusinessException(ErrorCode.SESSION_NOT_FOUND, "Session không tồn tại.")
            self._validate(project, session, data.expected_revision)
            session.choose_continuation(data.action)
            await dependencies.sessions.save(session)
            await dependencies.unit_of_work.commit()
        return await dependencies.state.read(project)

    @staticmethod
    def _validate(
        project: Project, session: ProjectSession, expected_revision: int
    ) -> None:
        if project.requirement_revision != expected_revision:
            raise BusinessException(
                ErrorCode.REQUIREMENT_REVISION_CONFLICT,
                "Requirement revision không còn hiện hành.",
            )
        valid_session = bool(
            session.project_id == project.id
            and session.purpose is SessionPurpose.REQUIREMENT_CLARIFICATION
            and session.status in {SessionStatus.ACTIVE, SessionStatus.COMPLETED}
            and session.base_requirement_revision == expected_revision
        )
        if not valid_session:
            raise BusinessException(ErrorCode.SESSION_PURPOSE_MISMATCH, "Sai Requirement session.")
        if session and (session.active_turn_id or session.pending_question_id):
            raise BusinessException(
                ErrorCode.REQUIREMENT_CONTINUATION_INVALID,
                "Requirement session chưa sẵn sàng để tiếp tục workflow.",
            )
        is_ready = project.analyzed_requirement_revision == project.requirement_revision
        if not is_ready:
            raise BusinessException(
                ErrorCode.REQUIREMENT_CONTINUATION_INVALID,
                "Structured Requirements chưa sẵn sàng.",
            )
