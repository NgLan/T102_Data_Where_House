"""Public ports của Data Model Analysis module."""

from abc import ABC, abstractmethod

from src.application.data_model_analysis.models import (
    AnalysisDocumentOutput,
    AnalysisSemanticInput,
    AnalysisSemanticOutput,
    GenerateAnalysisDocumentInput,
    ModelStructure,
)


class IDataModelStructureExtractor(ABC):
    @abstractmethod
    def extract(self, dbml: str) -> ModelStructure:
        """Parse DBML thành cấu trúc application độc lập thư viện."""


class IDataModelAnalysisService(ABC):
    @abstractmethod
    async def generate_document(self, data: GenerateAnalysisDocumentInput) -> AnalysisDocumentOutput:
        """Sinh tài liệu từ target Data Model và context hiện hành."""


class IDataModelAnalysisAgent(ABC):
    @abstractmethod
    async def analyze(self, data: AnalysisSemanticInput) -> AnalysisSemanticOutput:
        """Reason only about semantic mappings not determined by the DBML AST."""

    @abstractmethod
    async def repair(self, data: AnalysisSemanticInput, reason: str) -> AnalysisSemanticOutput:
        """Perform the single allowed structured-output repair attempt."""
