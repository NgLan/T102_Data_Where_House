"""Interface duy nhất của module Requirement."""

from abc import ABC, abstractmethod

from src.application.requirements.input import (
    AnalyzeRequirementClarificationInput,
    AnswerRequirementClarificationInput,
    ChooseRequirementContinuationInput,
    ClarifyRequirementsInput,
    DeleteRequirementInput,
    DeriveAnalyticalRequirementsInput,
    EvaluateSourceCoverageInput,
    GetRequirementClarificationInput,
    ListRequirementsInput,
    SendRequirementClarificationMessageInput,
)
from src.application.requirements.output import (
    AnalyticalDerivationResult,
    RequirementClarificationResult,
    RequirementClarificationStateOutput,
    RequirementOutput,
    SourceCoverageResult,
)


class IRequirementAnalysisAgent(ABC):
    """Outbound port cho clarification và analytical derivation."""

    @abstractmethod
    async def clarify_requirements(self, data: ClarifyRequirementsInput) -> RequirementClarificationResult:
        """Cấu trúc và làm rõ Requirement trong một Agent turn."""
        raise NotImplementedError

    @abstractmethod
    async def derive_analytical_requirements(
        self, data: DeriveAnalyticalRequirementsInput
    ) -> AnalyticalDerivationResult:
        """Sinh analytical requirements từ Requirement đã được duyệt."""
        raise NotImplementedError

    @abstractmethod
    async def evaluate_source_coverage(
        self, data: EvaluateSourceCoverageInput
    ) -> SourceCoverageResult:
        """Đánh giá source evidence sau khi Analytical Requirements đã sẵn sàng."""
        raise NotImplementedError


class IRequirementService(ABC):
    """Hợp đồng application cho các use case Requirement."""

    @abstractmethod
    async def list_requirements(self, data: ListRequirementsInput) -> list[RequirementOutput]:
        """Liệt kê toàn bộ yêu cầu của một dự án.

        Args:
            data: Project cần đọc yêu cầu.
        Returns:
            Danh sách yêu cầu nghiệp vụ.
        Raises:
            BusinessException: Khi actor không phải thành viên.
            InfrastructureException: Khi persistence thất bại.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_requirement(self, data: DeleteRequirementInput) -> None:
        """Xóa một Structured Requirement và làm outdated analytical output."""
        raise NotImplementedError

    @abstractmethod
    async def get_clarification(
        self, data: GetRequirementClarificationInput
    ) -> RequirementClarificationStateOutput: ...

    @abstractmethod
    async def analyze_clarification(
        self, data: AnalyzeRequirementClarificationInput
    ) -> RequirementClarificationStateOutput: ...

    @abstractmethod
    async def answer_clarification(
        self, data: AnswerRequirementClarificationInput
    ) -> RequirementClarificationStateOutput: ...

    @abstractmethod
    async def send_clarification_message(
        self, data: SendRequirementClarificationMessageInput
    ) -> RequirementClarificationStateOutput: ...

    @abstractmethod
    async def choose_clarification_continuation(
        self, data: ChooseRequirementContinuationInput
    ) -> RequirementClarificationStateOutput: ...
