"""Đồ thị LangGraph cho pipeline 4 agent sinh mô hình dữ liệu (T-019).

Cấu trúc bám theo Bước 2, 3 và 4 của `docs/guide_cho_ca_nhom/data_flow.md`:

    START → source_analysis → requirement_analysis → design → validate ─┬─ hợp lệ → END
                (SourceData)      (Requirement)      (DWDesign)  ↑      │
                                                                └─ retry ┘ sai cú pháp

Nối tuần tự vì RequirementAgent cần `Source Data đã được phân tích` do SourceDataAgent
sinh ra mới tạo được `AnalyticalRequirement`.
"""

from langchain_core.language_models import BaseChatModel
from langgraph.graph import END, START, StateGraph
from src.infrastructure.agents.constants import (
    DESIGN_NODE,
    REQUIREMENT_ANALYSIS_NODE,
    SOURCE_ANALYSIS_NODE,
    VALIDATE_NODE,
)
from src.infrastructure.agents.nodes.dw_design_agent import build_design_node
from src.infrastructure.agents.nodes.requirement_agent import (
    build_requirement_analysis_node,
)
from src.infrastructure.agents.nodes.source_analysis_agent import (
    build_source_analysis_node,
)
from src.infrastructure.agents.nodes.supervisor import build_validate_node, should_retry
from src.infrastructure.agents.state import DwPipelineState
from src.infrastructure.security.pii_guard import PiiGuard


def build_dw_pipeline_graph(chat_model: BaseChatModel, pii_guard: PiiGuard):
    """Dựng và biên dịch đồ thị pipeline 4 agent."""
    graph = StateGraph(DwPipelineState)

    graph.add_node(SOURCE_ANALYSIS_NODE, build_source_analysis_node(chat_model, pii_guard))
    graph.add_node(
        REQUIREMENT_ANALYSIS_NODE, build_requirement_analysis_node(chat_model, pii_guard)
    )
    graph.add_node(DESIGN_NODE, build_design_node(chat_model, pii_guard))
    graph.add_node(VALIDATE_NODE, build_validate_node(pii_guard))

    graph.add_edge(START, SOURCE_ANALYSIS_NODE)
    graph.add_edge(SOURCE_ANALYSIS_NODE, REQUIREMENT_ANALYSIS_NODE)
    graph.add_edge(REQUIREMENT_ANALYSIS_NODE, DESIGN_NODE)
    graph.add_edge(DESIGN_NODE, VALIDATE_NODE)
    graph.add_conditional_edges(
        VALIDATE_NODE,
        should_retry,
        {DESIGN_NODE: DESIGN_NODE, END: END},
    )

    return graph.compile()
