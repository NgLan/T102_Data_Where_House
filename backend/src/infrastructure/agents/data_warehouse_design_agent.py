"""DWDesignAgent provider-neutral cho generate và revise DBML."""

from src.application.data_warehouse_workflows.i_data_warehouse_workflow_service import (
    IDataWarehouseDesignAgent,
)
from src.application.data_warehouse_workflows.input import (
    ConversationDesignInput,
    DataWarehouseDesignInput,
    RevisionDesignInput,
)
from src.application.data_warehouse_workflows.output import ConversationDesignResult, GeneratedDbml, ValidationIssue
from src.common.logging import get_logger
from src.infrastructure.agents.agent_context_renderer import render_design_input
from src.infrastructure.agents.conversation_context_builder import (
    ConversationContextBuilder,
)
from src.infrastructure.agents.conversation_output_invoker import ConversationOutputInvoker
from src.infrastructure.agents.conversation_result_mapper import to_conversation_result
from src.infrastructure.agents.conversation_token_policy import ConversationTokenPolicy
from src.infrastructure.agents.dbml_normalizer import normalize_agent_dbml
from src.infrastructure.agents.prompts.dw_conversation import (
    DW_CONVERSATION_SYSTEM_PROMPT,
)
from src.infrastructure.agents.prompts.dw_design import (
    DW_DESIGN_SYSTEM_PROMPT,
    DW_DESIGN_USER_PROMPT,
)
from src.infrastructure.agents.prompts.dw_revise import (
    DW_REVISE_SYSTEM_PROMPT,
    DW_REVISE_USER_PROMPT,
)
from src.infrastructure.llm.agent_structured_outputs import (
    DbmlRevisionResult,
)
from src.infrastructure.llm.approximate_token_estimator import ApproximateTokenEstimator
from src.infrastructure.llm.lazy_chat_model import LazyLlmGateway, LlmGatewaySource
from src.infrastructure.llm.structured_llm_invoker import StructuredLlmInvoker
from src.infrastructure.security.pii_guard import PiiGuard
from typing_extensions import override

logger = get_logger(__name__)


class DataWarehouseDesignAgent(IDataWarehouseDesignAgent):
    """Mỗi method thực hiện đúng một structured LLM invocation."""

    def __init__(
        self,
        gateway: LlmGatewaySource,
        pii_guard: PiiGuard,
        context_builder: ConversationContextBuilder | None = None,
    ) -> None:
        self._gateway = LazyLlmGateway(gateway)
        self._pii_guard = pii_guard
        self._context_builder = context_builder or ConversationContextBuilder(
            ConversationTokenPolicy(32768, 8000), ApproximateTokenEstimator()
        )

    @override
    async def generate(self, data: DataWarehouseDesignInput) -> GeneratedDbml:
        """Sinh toàn bộ DBML từ ba nhóm context bắt buộc."""
        requirements, analytical, schemas = render_design_input(data)
        prompt = DW_DESIGN_USER_PROMPT.format(
            requirements=requirements,
            analytical_requirements=analytical,
            schema_metadata=schemas,
            failed_dbml=data.failed_dbml or "(none)",
            validation_issues=_render_issues(data.validation_issues),
        )
        return await self._invoke(DW_DESIGN_SYSTEM_PROMPT, prompt)

    @override
    async def revise(self, data: RevisionDesignInput) -> GeneratedDbml:
        """Sửa Current DBML bằng full project context."""
        requirements, analytical, schemas = render_design_input(data)
        prompt = DW_REVISE_USER_PROMPT.format(
            current_dbml=data.current_dbml,
            instruction=data.instruction or "Update the model to match current inputs.",
            requirements=requirements,
            analytical_requirements=analytical,
            schema_metadata=schemas,
            validation_issues=_render_issues(data.validation_issues),
        )
        return await self._invoke(DW_REVISE_SYSTEM_PROMPT, prompt)

    @override
    async def converse(self, data: ConversationDesignInput) -> ConversationDesignResult:
        """Trả câu hỏi làm rõ hoặc DBML proposal từ một structured invocation."""
        built = self._context_builder.build(data, DW_CONVERSATION_SYSTEM_PROMPT)
        logger.info(
            "conversation_context_allocated sections=%s soft_targets=%s retained_turns=%d dropped_turns=%d projection_tier=%d",
            built.section_tokens,
            built.soft_target_tokens,
            built.retained_turns,
            built.dropped_turns,
            built.projection_tier,
        )
        result = await ConversationOutputInvoker(self._gateway.get(), self._pii_guard).invoke(
            DW_CONVERSATION_SYSTEM_PROMPT, built.user_prompt
        )
        return to_conversation_result(result)

    async def _invoke(self, system_prompt: str, user_prompt: str) -> GeneratedDbml:
        """Gọi LLM một lần, unmask rồi chuẩn hóa DBML deterministic."""
        invoker = StructuredLlmInvoker(self._gateway.get(), self._pii_guard)
        result = await invoker.invoke(system_prompt, user_prompt, DbmlRevisionResult)
        return GeneratedDbml(normalize_agent_dbml(result.dbml))


def _render_issues(issues: tuple[ValidationIssue, ...]) -> str:
    """Render typed validation issues cho prompt retry."""
    lines = (f"[{item.severity}] {item.title}: {item.description}{_issue_location(item)}" for item in issues)
    return "\n".join(lines) or "(none)"


def _issue_location(issue: ValidationIssue) -> str:
    """Render vị trí lỗi bằng tên bảng/cột dễ đọc."""
    parts = tuple(item for item in (issue.table_name, issue.column_name) if item)
    return f" ({'.'.join(parts)})" if parts else ""
