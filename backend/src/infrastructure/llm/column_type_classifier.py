"""Structured LLM classifier cho các cột rule engine chưa chắc chắn."""

from src.application.data_sources.source_analysis_models import (
    ColumnClassificationInput,
    ColumnClassificationOutput,
)
from src.application.data_sources.source_analysis_ports import IColumnTypeClassifier
from src.common.utils.json import safe_json_dumps
from src.infrastructure.agents.prompts.grounding import PROJECT_EVIDENCE_POLICY
from src.infrastructure.llm.column_type_outputs import ColumnTypeClassificationResult
from src.infrastructure.llm.lazy_chat_model import LazyLlmGateway, LlmGatewaySource
from src.infrastructure.llm.structured_llm_invoker import StructuredLlmInvoker
from src.infrastructure.security.pii_guard import PiiGuard
from typing_extensions import override

SYSTEM_PROMPT = f"""You classify logical CSV column types.
{PROJECT_EVIDENCE_POLICY}

Use only each supplied column profile. Return exactly one result for every supplied opaque reference
and never invent, omit, or duplicate a reference. Choose only TEXT, CATEGORY, INTEGER, NUMBER,
DECIMAL, BOOLEAN, DATE, TIME, or DATETIME. Treat identifiers and free text conservatively. Sample
values are observations, not business definitions, guarantees, or database constraints."""
USER_PROMPT = "Classify these ambiguous column profiles:\n{columns}"
MAX_SAMPLE_LENGTH = 100
MAX_SAMPLES_PER_COLUMN = 10


class ColumnTypeClassifier(IColumnTypeClassifier):
    """Adapter provider-neutral, không phải một Agent workflow mới."""

    def __init__(self, gateway: LlmGatewaySource, pii_guard: PiiGuard) -> None:
        self._gateway = LazyLlmGateway(gateway)
        self._pii_guard = pii_guard

    @override
    async def classify(
        self,
        columns: tuple[ColumnClassificationInput, ...],
    ) -> tuple[ColumnClassificationOutput, ...]:
        """Gọi structured LLM đúng một lần cho một bounded batch."""
        if not columns:
            return ()
        result = await self._invoker().invoke(
            SYSTEM_PROMPT,
            USER_PROMPT.format(columns=safe_json_dumps(_prompt_payload(columns))),
            ColumnTypeClassificationResult,
        )
        return tuple(
            ColumnClassificationOutput(item.reference, item.data_type, item.confidence) for item in result.columns
        )

    def _invoker(self) -> StructuredLlmInvoker:
        return StructuredLlmInvoker(self._gateway.get(), self._pii_guard)


def _prompt_payload(
    columns: tuple[ColumnClassificationInput, ...],
) -> list[dict[str, object]]:
    return [
        {
            "reference": item.reference,
            "column_name": item.profile.name,
            "physical_type": item.profile.physical_type,
            "sample_values": [
                value[:MAX_SAMPLE_LENGTH] for value in item.profile.sample_values[:MAX_SAMPLES_PER_COLUMN]
            ],
            "null_ratio": _null_ratio(item),
            "distinct_count": item.profile.distinct_count,
            "distinct_ratio": item.profile.distinct_ratio,
            "average_length": item.profile.average_length,
            "candidate_type": item.candidate_type.value,
        }
        for item in columns
    ]


def _null_ratio(item: ColumnClassificationInput) -> float:
    return item.profile.null_count / item.profile.total_rows if item.profile.total_rows else 0
