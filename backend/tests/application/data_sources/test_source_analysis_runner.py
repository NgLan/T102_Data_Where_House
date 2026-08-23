"""Source runner chỉ gọi classifier khi cần và validate exact references."""

from uuid import uuid4

import pytest
from src.application.data_sources.source_analysis_models import (
    ColumnClassificationOutput,
    ProfiledSource,
    ProfiledTableSource,
    SourceFileAnalysisInput,
)
from src.application.data_sources.source_analysis_runner import SourceAnalysisRunner
from src.application.data_warehouse_workflows.source_analysis_runner import _ensure_source_revision
from src.common.exceptions.business import BusinessException
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.data_source.column_profile import ColumnProfile
from src.domain.data_source.enums import ColumnDataType


class Profiler:
    def __init__(self, columns: tuple[ColumnProfile, ...]) -> None:
        self.columns = columns

    def profile(self, content: bytes, filename: str) -> ProfiledSource:
        table = ProfiledTableSource(filename.removesuffix(".csv"), self.columns)
        return ProfiledSource((table,))


class Classifier:
    def __init__(self, invalid: bool = False) -> None:
        self.calls: list[int] = []
        self.invalid = invalid

    async def classify(self, columns):  # type: ignore[no-untyped-def]
        self.calls.append(len(columns))
        reference = "invalid" if self.invalid else None
        return tuple(
            ColumnClassificationOutput(reference or item.reference, ColumnDataType.TEXT, 0.9) for item in columns
        )


def ambiguous(name: str) -> ColumnProfile:
    return ColumnProfile(name, "VARCHAR", ("sample",), distinct_count=30, total_rows=100)


@pytest.mark.asyncio
async def test_classifier_batches_ambiguous_columns() -> None:
    classifier = Classifier()
    columns = tuple(ambiguous(f"column_{index}") for index in range(51))
    runner = SourceAnalysisRunner(Profiler(columns), classifier)
    result = await runner.analyze((SourceFileAnalysisInput(uuid4(), "source.csv", b"csv"),))
    assert classifier.calls == [50, 1]
    assert len(result[0].schema_metadata.tables[0].columns) == 51


@pytest.mark.asyncio
async def test_confident_rule_does_not_call_classifier() -> None:
    classifier = Classifier()
    runner = SourceAnalysisRunner(Profiler((ColumnProfile("customer_id", "BIGINT"),)), classifier)
    await runner.analyze((SourceFileAnalysisInput(uuid4(), "source.csv", b"csv"),))
    assert classifier.calls == []


@pytest.mark.asyncio
async def test_invalid_classifier_reference_is_rejected() -> None:
    runner = SourceAnalysisRunner(Profiler((ambiguous("value"),)), Classifier(invalid=True))
    with pytest.raises(InfrastructureException):
        await runner.analyze((SourceFileAnalysisInput(uuid4(), "source.csv", b"csv"),))


def test_stale_source_revision_is_rejected_before_persist() -> None:
    with pytest.raises(BusinessException):
        _ensure_source_revision(current=2, expected=1)
