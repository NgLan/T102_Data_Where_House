"""Outbound ports cho CSV profiling và logical type classification."""

from typing import Protocol

from src.application.data_sources.source_analysis_models import (
    ColumnClassificationInput,
    ColumnClassificationOutput,
    ProfiledCsvSource,
)


class ICsvDataProfiler(Protocol):
    """Port profile CSV bằng implementation hạ tầng."""

    def profile(self, file_bytes: bytes, filename: str) -> ProfiledCsvSource:
        """Trả typed/raw profile nhưng chưa quyết định final data type."""
        ...


class IColumnTypeClassifier(Protocol):
    """Port structured LLM cho các cột rule engine chưa chắc chắn."""

    async def classify(
        self,
        columns: tuple[ColumnClassificationInput, ...],
    ) -> tuple[ColumnClassificationOutput, ...]:
        """Phân loại một batch metadata cột giới hạn."""
        ...
