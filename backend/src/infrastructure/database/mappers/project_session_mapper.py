"""Mapper chuyển đổi dữ liệu giữa ProjectSession Domain Entity và ProjectSessionModel Persistence."""

from src.domain.project_session.entities import ProjectSession
from src.domain.project_session.enums import (
    RequirementContinuationState,
    SessionPurpose,
    SessionStatus,
)
from src.infrastructure.database.mappers.conversation_summary_codec import (
    decode_conversation_summary,
    encode_conversation_summary,
)
from src.infrastructure.database.models.project_session import ProjectSessionModel


class ProjectSessionMapper:
    """Mapper thực hiện chuyển đổi giữa ProjectSession Entity và ProjectSessionModel."""

    @staticmethod
    def to_domain(model: ProjectSessionModel) -> ProjectSession:
        """Chuyển đổi từ ProjectSessionModel (Persistence) sang ProjectSession (Domain Entity)."""
        return ProjectSession(
            id=model.id,
            project_id=model.project_id,
            user_id=model.user_id,
            title=model.title or "Untitled Session",
            status=SessionStatus(model.status),
            purpose=SessionPurpose(model.purpose),
            base_requirement_revision=model.base_requirement_revision,
            requirement_continuation_state=RequirementContinuationState(
                model.requirement_continuation_state
            ),
            active_turn_id=model.active_turn_id,
            active_turn_started_at=model.active_turn_started_at,
            pending_question_id=model.pending_question_id,
            conversation_summary=decode_conversation_summary(model.conversation_summary),
            summarized_through_event_id=model.summarized_through_event_id,
            summary_updated_at=model.summary_updated_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: ProjectSession) -> ProjectSessionModel:
        """Chuyển đổi từ ProjectSession (Domain Entity) sang ProjectSessionModel (Persistence)."""
        return ProjectSessionModel(
            id=entity.id,
            project_id=entity.project_id,
            user_id=entity.user_id,
            title=entity.title,
            status=entity.status.value,
            purpose=entity.purpose.value,
            base_requirement_revision=entity.base_requirement_revision,
            requirement_continuation_state=entity.requirement_continuation_state.value,
            active_turn_id=entity.active_turn_id,
            active_turn_started_at=entity.active_turn_started_at,
            pending_question_id=entity.pending_question_id,
            conversation_summary=encode_conversation_summary(entity.conversation_summary),
            summarized_through_event_id=entity.summarized_through_event_id,
            summary_updated_at=entity.summary_updated_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def update_model(model: ProjectSessionModel, entity: ProjectSession) -> ProjectSessionModel:
        """Cập nhật dữ liệu từ ProjectSession Entity sang ProjectSessionModel đã tồn tại."""
        model.project_id = entity.project_id
        model.user_id = entity.user_id
        model.title = entity.title
        model.status = entity.status.value
        model.purpose = entity.purpose.value
        model.base_requirement_revision = entity.base_requirement_revision
        model.requirement_continuation_state = (
            entity.requirement_continuation_state.value
        )
        model.active_turn_id = entity.active_turn_id
        model.active_turn_started_at = entity.active_turn_started_at
        model.pending_question_id = entity.pending_question_id
        model.conversation_summary = encode_conversation_summary(entity.conversation_summary)
        model.summarized_through_event_id = entity.summarized_through_event_id
        model.summary_updated_at = entity.summary_updated_at
        model.updated_at = entity.updated_at
        return model
