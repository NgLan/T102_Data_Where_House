"""Public service contract của Data Model module."""

from abc import ABC, abstractmethod

from src.application.data_models.input import (
    ChangeProposalIdInput,
    GenerateDataModelDdlInput,
    GetChangeProposalInput,
    GetDataModelInput,
    GetPendingChangeProposalInput,
    ResolveDataModelTargetInput,
    UpdateDataModelInput,
    ValidateDataModelInput,
)
from src.application.data_models.output import (
    ChangeProposalDetailOutput,
    ChangeProposalSummaryOutput,
    DataModelDdlOutput,
    DataModelOutput,
    ResolvedDataModelTargetOutput,
)
from src.application.data_warehouse_workflows.output import ValidationIssue
from src.domain.sandbox.enums import SandboxDbType


class IDataModelDdlGenerator(ABC):
    """Outbound port biên dịch DBML sang DDL."""

    @abstractmethod
    def generate_ddl(self, dbml: str, db_type: SandboxDbType) -> str:
        """Sinh DDL cho database type được yêu cầu."""
        raise NotImplementedError


class IDataModelService(ABC):
    """Hợp đồng lifecycle của snapshot và Human Review."""

    @abstractmethod
    async def get_data_model(self, data: GetDataModelInput) -> DataModelOutput:
        """Lấy snapshot cùng trạng thái outdated được tính từ revision."""

    @abstractmethod
    async def update_data_model(self, data: UpdateDataModelInput) -> DataModelOutput:
        """Lưu trực tiếp chỉnh sửa thủ công bằng optimistic locking."""

    @abstractmethod
    async def get_validation_issues(self, data: GetDataModelInput) -> tuple[ValidationIssue, ...]:
        """Validate snapshot hiện hành bằng ValidationEngine dùng chung."""

    @abstractmethod
    async def validate_draft(self, data: ValidateDataModelInput) -> tuple[ValidationIssue, ...]:
        """Kiểm tra DBML draft mà không thay đổi snapshot."""

    @abstractmethod
    async def get_change_proposal(self, data: GetChangeProposalInput) -> ChangeProposalDetailOutput:
        """Lấy proposal cùng snapshot hiện hành."""

    @abstractmethod
    async def get_pending_change_proposal(
        self, data: GetPendingChangeProposalInput
    ) -> ChangeProposalDetailOutput | None:
        """Return the actor's pending proposal for a project, when present."""

    @abstractmethod
    async def accept_change_proposal(self, data: ChangeProposalIdInput) -> DataModelOutput:
        """Áp dụng proposal còn hợp lệ."""

    @abstractmethod
    async def reject_change_proposal(self, data: ChangeProposalIdInput) -> ChangeProposalSummaryOutput:
        """Chuyển proposal đang chờ sang REJECTED."""

    @abstractmethod
    async def generate_ddl(self, data: GenerateDataModelDdlInput) -> DataModelDdlOutput:
        """Sinh DDL từ snapshot Data Model hiện hành."""

    @abstractmethod
    async def resolve_target(
        self, data: ResolveDataModelTargetInput
    ) -> ResolvedDataModelTargetOutput:
        """Resolve current/proposal target sau authorization."""
