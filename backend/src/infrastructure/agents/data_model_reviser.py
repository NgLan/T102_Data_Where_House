"""Adapter nối cổng IDataModelReviser của tầng Domain với đồ thị LangGraph."""

from langchain_core.language_models import BaseChatModel
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.logging import get_logger
from src.domain.data_model.revision import DbmlRevisionProposal, IDataModelReviser
from src.infrastructure.agents.state import DwDesignState
from src.infrastructure.agents.workflows.dw_design import build_dw_design_graph
from src.infrastructure.security.pii_guard import PiiGuard

logger = get_logger(__name__)


class LangGraphDataModelReviser(IDataModelReviser):
    """Chỉnh sửa mô hình dữ liệu bằng đồ thị LangGraph (Agent điều phối + DWDesignAgent)."""

    def __init__(self, chat_model: BaseChatModel, pii_guard: PiiGuard) -> None:
        """Khởi tạo adapter và biên dịch sẵn đồ thị."""
        self._graph = build_dw_design_graph(chat_model, pii_guard)

    async def revise(self, current_dbml: str, instruction: str) -> DbmlRevisionProposal:
        """Sinh phiên bản DBML mới từ DBML hiện tại và yêu cầu ngôn ngữ tự nhiên."""
        initial_state: DwDesignState = {
            "current_dbml": current_dbml,
            "instruction": instruction,
            "attempts": 0,
            "validation_error": "",
        }

        final_state: DwDesignState = await self._graph.ainvoke(initial_state)

        validation_error = final_state.get("validation_error", "")
        if validation_error:
            logger.error(
                "ai_revision_failed attempts=%d error=%s",
                final_state.get("attempts", 0),
                validation_error,
            )
            raise BusinessException(
                code=ErrorCode.INVALID_DBML_CONTENT,
                message=(
                    "AI Agent không sinh được mô hình DBML hợp lệ sau "
                    f"{final_state.get('attempts', 0)} lần thử. Vui lòng diễn đạt lại yêu cầu."
                ),
            )

        logger.info(
            "ai_revision_completed attempts=%d changed_tables=%s",
            final_state.get("attempts", 0),
            final_state.get("changed_tables", []),
        )
        return DbmlRevisionProposal(
            dbml=final_state["proposed_dbml"],
            summary=final_state.get("summary", ""),
            changed_tables=final_state.get("changed_tables", []),
            attempts=final_state.get("attempts", 0),
        )
