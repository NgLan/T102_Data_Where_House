"""Đồ thị LangGraph cho luồng chỉnh sửa mô hình dữ liệu bằng AI (T-024).

Cấu trúc đồ thị bám theo Bước 3 và Bước 4 của `docs/guide_cho_ca_nhom/data_flow.md`:

    START → design (DWDesignAgent) → validate (ValidationEngine)
                ↑                          │
                └──── retry khi sai ───────┴──── hợp lệ / hết lượt → END
"""

from langchain_core.language_models import BaseChatModel
from langgraph.graph import END, START, StateGraph
from src.infrastructure.agents.constants import DESIGN_NODE, VALIDATE_NODE
from src.infrastructure.agents.nodes.dw_design_agent import build_design_node
from src.infrastructure.agents.nodes.supervisor import build_validate_node, should_retry
from src.infrastructure.agents.state import DwDesignState
from src.infrastructure.security.pii_guard import PiiGuard


def build_dw_design_graph(chat_model: BaseChatModel, pii_guard: PiiGuard):
    """Dựng và biên dịch đồ thị chỉnh sửa mô hình dữ liệu."""
    graph = StateGraph(DwDesignState)

    graph.add_node(DESIGN_NODE, build_design_node(chat_model, pii_guard))
    graph.add_node(VALIDATE_NODE, build_validate_node(pii_guard))

    graph.add_edge(START, DESIGN_NODE)
    graph.add_edge(DESIGN_NODE, VALIDATE_NODE)
    graph.add_conditional_edges(
        VALIDATE_NODE,
        should_retry,
        {DESIGN_NODE: DESIGN_NODE, END: END},
    )

    return graph.compile()
