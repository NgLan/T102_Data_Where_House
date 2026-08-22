"""Điều phối profiler, Domain rules và classifier cho source pending."""

from src.application.data_sources.source_analysis_models import (
    AnalyzedSourceSchema,
    ColumnClassificationInput,
    ColumnClassificationOutput,
    ProfiledCsvSource,
    SourceFileAnalysisInput,
)
from src.application.data_sources.source_analysis_ports import (
    IColumnTypeClassifier,
    ICsvDataProfiler,
)
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.data_source.column_profile import ColumnProfile, LogicalTypeDecision
from src.domain.data_source.column_type_inference import (
    infer_logical_type,
    is_identifier_like,
)
from src.domain.data_source.enums import ColumnDataType
from src.domain.data_source.value_objects import ColumnMetadata, SchemaMetadata, TableMetadata

RULE_CLASSIFIER_THRESHOLD = 0.8
CLASSIFIER_FALLBACK_THRESHOLD = 0.7
MAX_CLASSIFIER_BATCH_SIZE = 50


class SourceAnalysisRunner:
    """Tạo SchemaMetadata cuối cùng cho một batch source."""

    def __init__(
        self,
        profiler: ICsvDataProfiler,
        classifier: IColumnTypeClassifier,
    ) -> None:
        self._profiler = profiler
        self._classifier = classifier

    async def analyze(
        self,
        sources: tuple[SourceFileAnalysisInput, ...],
    ) -> tuple[AnalyzedSourceSchema, ...]:
        """Profile toàn bộ source và chỉ classify các cột ambiguous."""
        profiles = tuple(self._profiler.profile(item.content, item.filename) for item in sources)
        decisions = tuple(tuple(infer_logical_type(column) for column in item.columns) for item in profiles)
        classifications = await self._classify_ambiguous(profiles, decisions)
        return tuple(
            _build_source_schema(index, source, profile, decision, classifications)
            for index, (source, profile, decision) in enumerate(zip(sources, profiles, decisions, strict=True))
        )

    async def _classify_ambiguous(
        self,
        profiles: tuple[ProfiledCsvSource, ...],
        decisions: tuple[tuple[LogicalTypeDecision, ...], ...],
    ) -> dict[str, ColumnClassificationOutput]:
        inputs = _classification_inputs(profiles, decisions)
        outputs: dict[str, ColumnClassificationOutput] = {}
        for start in range(0, len(inputs), MAX_CLASSIFIER_BATCH_SIZE):
            batch = inputs[start : start + MAX_CLASSIFIER_BATCH_SIZE]
            classified = await self._classifier.classify(batch)
            _validate_classifications(batch, classified)
            outputs.update((item.reference, item) for item in classified)
        return outputs


def _classification_inputs(
    profiles: tuple[ProfiledCsvSource, ...],
    decisions: tuple[tuple[LogicalTypeDecision, ...], ...],
) -> tuple[ColumnClassificationInput, ...]:
    inputs = []
    for source_index, (profile, source_decisions) in enumerate(zip(profiles, decisions, strict=True)):
        for column_index, (column, decision) in enumerate(zip(profile.columns, source_decisions, strict=True)):
            if decision.confidence < RULE_CLASSIFIER_THRESHOLD:
                inputs.append(ColumnClassificationInput(f"{source_index}:{column_index}", column, decision.data_type))
    return tuple(inputs)


def _validate_classifications(
    inputs: tuple[ColumnClassificationInput, ...],
    outputs: tuple[ColumnClassificationOutput, ...],
) -> None:
    expected = {item.reference for item in inputs}
    actual = [item.reference for item in outputs]
    if set(actual) != expected or len(actual) != len(set(actual)):
        raise InfrastructureException(ErrorCode.LLM_ERROR, "Classifier trả reference cột không hợp lệ.")


def _build_source_schema(
    source_index: int,
    source: SourceFileAnalysisInput,
    profile: ProfiledCsvSource,
    decisions: tuple[LogicalTypeDecision, ...],
    classifications: dict[str, ColumnClassificationOutput],
) -> AnalyzedSourceSchema:
    columns = tuple(
        _build_column(column, decision, classifications.get(f"{source_index}:{column_index}"))
        for column_index, (column, decision) in enumerate(zip(profile.columns, decisions, strict=True))
    )
    schema = SchemaMetadata(tables=(TableMetadata(profile.table_name, columns),))
    return AnalyzedSourceSchema(source.source_id, schema)


def _build_column(
    profile: ColumnProfile,
    decision: LogicalTypeDecision,
    classification: ColumnClassificationOutput | None,
) -> ColumnMetadata:
    final_type = decision.data_type
    if classification and classification.confidence >= CLASSIFIER_FALLBACK_THRESHOLD:
        final_type = classification.data_type
    non_null_count = profile.total_rows - profile.null_count
    is_unique = non_null_count > 0 and profile.distinct_count == non_null_count
    return ColumnMetadata(
        name=profile.name,
        data_type=final_type,
        nullable=profile.null_count > 0,
        null_count=profile.null_count,
        distinct_count=profile.distinct_count,
        distinct_values=profile.distinct_values if final_type is ColumnDataType.CATEGORY else (),
        is_unique_candidate=is_unique,
        is_key_candidate=is_unique and is_identifier_like(profile),
    )
