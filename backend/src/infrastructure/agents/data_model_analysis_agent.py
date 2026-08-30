"""Structured semantic analysis Agent with no persistence responsibility."""

from dataclasses import asdict

from src.application.data_model_analysis.i_data_model_analysis_service import IDataModelAnalysisAgent
from src.application.data_model_analysis.models import (
    AnalysisSemanticInput,
    AnalysisSemanticOutput,
    SemanticObservation,
)
from src.common.utils.json import safe_json_dumps
from src.infrastructure.agents.prompts.data_model_analysis import (
    ANALYSIS_REPAIR_PROMPT,
    ANALYSIS_SYSTEM_PROMPT,
)
from src.infrastructure.llm.data_model_analysis_output import DataModelAnalysisAgentOutput
from src.infrastructure.llm.lazy_chat_model import LazyLlmGateway, LlmGatewaySource
from src.infrastructure.llm.structured_llm_invoker import StructuredLlmInvoker
from src.infrastructure.security.pii_guard import PiiGuard
from typing_extensions import override


class DataModelAnalysisAgent(IDataModelAnalysisAgent):
    """Gọi LLM structured-output cho phần reasoning ngữ nghĩa đã được giới hạn."""

    def __init__(self, gateway: LlmGatewaySource, pii_guard: PiiGuard) -> None:
        self._gateway = LazyLlmGateway(gateway)
        self._pii_guard = pii_guard

    @override
    async def analyze(self, data: AnalysisSemanticInput) -> AnalysisSemanticOutput:
        return await self._invoke(data, "")

    @override
    async def repair(self, data: AnalysisSemanticInput, reason: str) -> AnalysisSemanticOutput:
        instruction = ANALYSIS_REPAIR_PROMPT.format(reason=reason)
        return await self._invoke(data, instruction)

    async def _invoke(self, data: AnalysisSemanticInput, repair_instruction: str) -> AnalysisSemanticOutput:
        prompt = safe_json_dumps(asdict(data), indent=2)
        if repair_instruction:
            prompt = f"{prompt}\n\n{repair_instruction}"
        output = await StructuredLlmInvoker(self._gateway.get(), self._pii_guard).invoke(
            ANALYSIS_SYSTEM_PROMPT, prompt, DataModelAnalysisAgentOutput
        )
        return AnalysisSemanticOutput(
            tuple(
                SemanticObservation(
                    item.explanation,
                    item.evidence,
                    item.table_name,
                    item.column_name,
                    item.requirement_id,
                    item.source_id,
                )
                for item in output.observations
            ),
            tuple(output.uncertainties),
        )
