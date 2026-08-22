"""Thực thể Data Model và re-export đề xuất thay đổi tương thích."""

from dataclasses import dataclass

from src.common.exceptions.business import BusinessException
from src.domain.data_model.data_model_change import DataModelChange
from src.domain.data_model.data_model_change_rules import (
    INITIAL_DATA_MODEL_REVISION,
    validate_change_status_transition,
    validate_revision,
    validate_revision_match,
)
from src.domain.data_model.dbml_syntax_rules import validate_dbml
from src.domain.data_model.enums import DataModelChangeStatus
from src.domain.shared.entity import BaseEntity
from src.domain.shared.types import EntityID


@dataclass(eq=False, kw_only=True)
class DataModel(BaseEntity):
    """Snapshot DBML có revision thuộc một Project."""

    project_id: EntityID
    dbml: str
    revision: int = INITIAL_DATA_MODEL_REVISION
    generated_from_requirement_revision: int = INITIAL_DATA_MODEL_REVISION
    generated_from_source_revision: int = INITIAL_DATA_MODEL_REVISION

    def __post_init__(self) -> None:
        """Kiểm tra DBML và revision khi khởi tạo."""
        super().__post_init__()
        validate_dbml(self.dbml)
        validate_revision(self.revision)

    def apply_change(self, change: DataModelChange) -> None:
        """Áp dụng đề xuất bằng optimistic concurrency control.

        Args:
            change: Đề xuất đang ở trạng thái PROPOSED.

        Raises:
            BusinessException: Khi trạng thái, revision hoặc DBML không hợp lệ.
        """
        validate_change_status_transition(change.status, DataModelChangeStatus.ACCEPTED)
        try:
            validate_revision_match(change.base_revision, self.revision)
        except BusinessException:
            change.mark_conflicted()
            raise
        validate_dbml(change.proposed_dbml)
        self.dbml = change.proposed_dbml
        self.revision += 1
        self.mark_updated()
        change.mark_accepted()

    def record_generation_revisions(
        self, requirement_revision: int, source_revision: int
    ) -> None:
        """Ghi nhận analysis revisions tạo nên snapshot hiện tại.

        Args:
            requirement_revision: Requirement analysis revision đã dùng.
            source_revision: Source analysis revision đã dùng.
        """
        self.generated_from_requirement_revision = requirement_revision
        self.generated_from_source_revision = source_revision

    def update_dbml(self, dbml: str, base_revision: int) -> None:
        """Cập nhật DBML khi base revision còn hiện hành.

        Args:
            dbml: Snapshot DBML thay thế.
            base_revision: Revision caller đã đọc.

        Raises:
            BusinessException: Khi revision lệch hoặc DBML không hợp lệ.
        """
        validate_revision_match(base_revision, self.revision)
        validate_dbml(dbml)
        self.dbml = dbml
        self.revision += 1
        self.mark_updated()

    def is_outdated(self, requirement_revision: int, source_revision: int) -> bool:
        """Kiểm tra model có được sinh từ analysis revision hiện tại không."""
        return (
            self.generated_from_requirement_revision != requirement_revision
            or self.generated_from_source_revision != source_revision
        )


__all__ = ["DataModel", "DataModelChange"]
