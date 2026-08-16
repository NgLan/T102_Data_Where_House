"""LLM Data Model analysis with structured output and a rule-based fallback."""

import json
from typing import Any, Literal, Protocol

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

try:
    from pydbml import PyDBML
except ImportError:
    PyDBML = None  # type: ignore
from src.application.data_models.artifact_generator import IDataModelArtifactGenerator
from src.application.data_models.insight_analyzer import IDataModelInsightAnalyzer
from src.application.data_models.output import DataModelInsightOutput
from src.common.logging import get_logger
from typing_extensions import override

logger = get_logger(__name__)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

SYSTEM_PROMPT = """Bạn là chuyên gia thiết kế data warehouse đang thẩm định một schema DBML.
Chỉ sử dụng các sự kiện cấu trúc trong JSON được cung cấp; không tự tạo bảng, cột, khóa hay quan hệ.
Phân tích grain, primary key, foreign key/cardinality, fact-dimension, index, tên và kiểu dữ liệu.
Trả lời bằng tiếng Việt, ngắn gọn, có căn cứ cụ thể và khuyến nghị có thể hành động.
Mỗi insight phải dùng đúng table_name trong danh sách, severity là info/warn/error,
confidence trong khoảng 0..1 và id theo dạng <table>:<short-code>.
Tối đa 3 insight quan trọng nhất cho mỗi bảng."""


class LlmDataModelInsight(BaseModel):
    """Structured output for one LLM-generated insight."""

    id: str = Field(min_length=1)
    table_name: str = Field(min_length=1)
    severity: Literal["info", "warn", "error"]
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    evidence: list[str] = Field(default_factory=list)
    recommendation: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)


class LlmDataModelInsightBatch(BaseModel):
    """Envelope used to keep the model response schema stable."""

    insights: list[LlmDataModelInsight]


class AsyncStructuredLlm(Protocol):
    """Small interface shared by LangChain structured runnables and test doubles."""

    async def ainvoke(self, input: Any) -> Any:
        """Invoke the model asynchronously."""
        ...


class LlmDataModelInsightAnalyzer(IDataModelInsightAnalyzer):
    """Use an LLM for T-028 and fall back to PyDBML when it is unavailable."""

    def __init__(
        self,
        fallback: IDataModelArtifactGenerator,
        *,
        api_key: str = "",
        base_url: str = "",
        model_name: str = "gpt-4o-mini",
        max_tokens: int = 2000,
        llm: AsyncStructuredLlm | None = None,
        minimum_confidence: float = 0.5,
    ) -> None:
        self._fallback = fallback
        self._minimum_confidence = minimum_confidence
        self._llm = llm or self._create_llm(api_key, base_url, model_name, max_tokens)

    @override
    async def analyze(self, dbml: str) -> list[DataModelInsightOutput]:
        # Building the fallback first validates DBML and guarantees a useful response.
        fallback_insights = self._fallback.analyze(dbml)
        if self._llm is None:
            return fallback_insights

        schema_context = self._extract_schema_context(dbml)
        try:
            raw_result = await self._llm.ainvoke(
                [
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(content=json.dumps(schema_context, ensure_ascii=False)),
                ]
            )
            result = LlmDataModelInsightBatch.model_validate(raw_result)
            grounded = self._ground_insights(result, schema_context["tables"])
            return grounded or fallback_insights
        except Exception as exc:
            logger.warning("T-028 LLM analysis failed; using rule-based fallback: %s", exc)
            return fallback_insights

    @staticmethod
    def _create_llm(
        api_key: str,
        base_url: str,
        model_name: str,
        max_tokens: int,
    ) -> AsyncStructuredLlm | None:
        normalized_key = api_key.strip()
        normalized_base_url = base_url.strip()

        is_local = (
            "localhost" in normalized_base_url
            or "127.0.0.1" in normalized_base_url
            or normalized_key.lower() in ("ollama", "local", "lmstudio")
        )

        if not is_local and (not normalized_key or normalized_key.lower().startswith(("sk-placeholder", "sk-your-"))):
            return None

        effective_key = normalized_key if (normalized_key and not normalized_key.lower().startswith(("sk-placeholder", "sk-your-"))) else "ollama"

        from langchain_openai import ChatOpenAI

        resolved_base_url, resolved_model_name = LlmDataModelInsightAnalyzer._resolve_provider_config(
            effective_key,
            normalized_base_url,
            model_name,
        )
        model_options: dict[str, Any] = dict(
            api_key=normalized_key,
            model=resolved_model_name,
            temperature=0,
            max_tokens=max_tokens,
            timeout=30,
            max_retries=1,
        )
        if resolved_base_url:
            model_options["base_url"] = resolved_base_url
        model = ChatOpenAI(**model_options)
        return model.with_structured_output(LlmDataModelInsightBatch)

    @staticmethod
    def _resolve_provider_config(api_key: str, base_url: str, model_name: str) -> tuple[str, str]:
        resolved_base_url = base_url.strip().rstrip("/")
        if not resolved_base_url and api_key.lower().startswith("sk-or-v1-"):
            resolved_base_url = OPENROUTER_BASE_URL

        resolved_model_name = model_name.strip()
        is_openrouter = resolved_base_url.casefold() == OPENROUTER_BASE_URL.casefold()
        openai_model_prefixes = ("gpt-", "chatgpt-", "o1", "o3", "o4")
        if is_openrouter and "/" not in resolved_model_name and resolved_model_name.startswith(openai_model_prefixes):
            resolved_model_name = f"openai/{resolved_model_name}"
        return resolved_base_url, resolved_model_name

    @staticmethod
    def _extract_schema_context(dbml: str) -> dict[str, Any]:
        database = PyDBML(dbml)
        tables = []
        for table in database.tables:
            tables.append(
                {
                    "name": table.name,
                    "columns": [
                        {
                            "name": column.name,
                            "type": str(column.type),
                            "primary_key": bool(column.pk),
                            "not_null": bool(column.not_null),
                            "unique": bool(column.unique),
                        }
                        for column in table.columns
                    ],
                    "indexes": [
                        {
                            "columns": [getattr(subject, "name", str(subject)) for subject in index.subjects],
                            "unique": bool(index.unique),
                        }
                        for index in table.indexes
                    ],
                }
            )

        relationships = [
            {
                "type": reference.type,
                "from": [{"table": column.table.name, "column": column.name} for column in reference.col1],
                "to": [{"table": column.table.name, "column": column.name} for column in reference.col2],
            }
            for reference in database.refs
        ]
        return {"tables": tables, "relationships": relationships}

    def _ground_insights(
        self,
        result: LlmDataModelInsightBatch,
        tables: list[dict[str, Any]],
    ) -> list[DataModelInsightOutput]:
        canonical_names = {table["name"].casefold(): table["name"] for table in tables}
        grounded: list[DataModelInsightOutput] = []
        seen_ids: set[str] = set()

        for insight in result.insights:
            table_name = canonical_names.get(insight.table_name.casefold())
            insight_id = insight.id.strip()
            if table_name is None or insight.confidence < self._minimum_confidence or insight_id in seen_ids:
                continue
            seen_ids.add(insight_id)
            grounded.append(
                DataModelInsightOutput(
                    id=insight_id,
                    table_name=table_name,
                    severity=insight.severity,
                    title=insight.title.strip(),
                    description=self._format_description(insight),
                )
            )
        return grounded

    @staticmethod
    def _format_description(insight: LlmDataModelInsight) -> str:
        parts = [insight.description.strip()]
        evidence = [item.strip() for item in insight.evidence if item.strip()]
        if evidence:
            parts.append("Căn cứ: " + "; ".join(evidence))
        if insight.recommendation and insight.recommendation.strip():
            parts.append("Khuyến nghị: " + insight.recommendation.strip())
        return " ".join(parts)
