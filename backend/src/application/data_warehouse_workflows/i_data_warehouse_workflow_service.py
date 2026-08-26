"""Public service contract và outbound ports của workflow kho dữ liệu."""

from abc import ABC, abstractmethod

from src.application.data_models.output import ChangeProposalDetailOutput, DataModelOutput
from src.application.data_warehouse_workflows.input import (
    ConversationDesignInput,
    CreateAgentTurnInput,
    CreateAiEditProposalInput,
    DataWarehouseDesignInput,
    GenerateDataModelInput,
    GetAnalysisStatusInput,
    GetSourceCoverageInput,
    ReanalyzeProjectInput,
    RecheckSourceCoverageInput,
    RegenerateDataModelInput,
    ResolveSourceCoverageInput,
    RevisionDesignInput,
)
from src.application.data_warehouse_workflows.output import (
    AgentTurnOutput,
    AnalysisStatusOutput,
    ConversationDesignResult,
    GeneratedDbml,
    ValidationIssue,
)


class IDataWarehouseDesignAgent(ABC):
    """Outbound port cho các operation của DWDesignAgent."""

    @abstractmethod
    async def generate(self, data: DataWarehouseDesignInput) -> GeneratedDbml:
        """Sinh DBML ban đầu bằng đúng một LLM invocation."""

    @abstractmethod
    async def revise(self, data: RevisionDesignInput) -> GeneratedDbml:
        """Sinh DBML đề xuất bằng đúng một LLM invocation."""
    @abstractmethod
    async def converse(self, data: ConversationDesignInput) -> ConversationDesignResult:
        """Trả câu hỏi làm rõ hoặc DBML proposal trong một invocation."""


class IDataModelValidationEngine(ABC):
    """Outbound port cho ValidationEngine deterministic."""

    @abstractmethod
    def validate(self, dbml: str) -> tuple[ValidationIssue, ...]:
        """Trả toàn bộ lỗi và cảnh báo của DBML."""


class IDataWarehouseWorkflowService(ABC):
    """Hợp đồng điều phối workflow từ action rõ ràng của người dùng."""

    @abstractmethod
    async def get_analysis_status(self, data: GetAnalysisStatusInput) -> AnalysisStatusOutput:
        """Đọc trạng thái đồng bộ mà không gọi Agent."""

    @abstractmethod
    async def get_source_coverage(self, data: GetSourceCoverageInput) -> AnalysisStatusOutput:
        """Reload persisted coverage state without invoking an Agent."""

    @abstractmethod
    async def resolve_source_coverage(
        self, data: ResolveSourceCoverageInput
    ) -> AnalysisStatusOutput:
        """Persist one Source Confirmation item without invoking an Agent."""

    @abstractmethod
    async def recheck_source_coverage(
        self, data: RecheckSourceCoverageInput
    ) -> AnalysisStatusOutput:
        """Materialize a completed batch and rerun only Source Coverage."""

    @abstractmethod
    async def generate_data_model(self, data: GenerateDataModelInput) -> DataModelOutput:
        """Phân tích input và tạo Data Model đầu tiên."""

    @abstractmethod
    async def synchronize_data_model(
        self, data: GenerateDataModelInput
    ) -> DataModelOutput:
        """Tạo, cập nhật hoặc reuse Data Model theo analysis hiện hành."""

    @abstractmethod
    async def reanalyze(self, data: ReanalyzeProjectInput) -> AnalysisStatusOutput:
        """Phân tích input đã đổi nhưng không sửa Data Model."""

    @abstractmethod
    async def regenerate_data_model(self, data: RegenerateDataModelInput) -> DataModelOutput:
        """Tạo lại và ghi đè Data Model hiện hành sau validation."""

    @abstractmethod
    async def create_agent_turn(self, data: CreateAgentTurnInput) -> AgentTurnOutput:
        """Tạo lượt hội thoại có thể trả clarification hoặc proposal."""

    @abstractmethod
    async def create_ai_edit_proposal(self, data: CreateAiEditProposalInput) -> ChangeProposalDetailOutput:
        """Tạo proposal AI edit để Human Review."""
