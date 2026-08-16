"""State schema dùng chung cho các đồ thị LangGraph của hệ thống AI Agent."""

"""State schema dùng chung cho các đồ thị LangGraph của hệ thống AI Agent."""

from __future__ import annotations

from typing import TypedDict

from src.infrastructure.llm.models import (
    AnalyticalRequirementItem,
    SourceSchemaResult,
)


class DwPipelineState(TypedDict, total=False):
    """State của pipeline 4 agent sinh mô hình dữ liệu (T-019).

    Mỗi node đọc và ghi vào state này. `total=False` cho phép mọi trường là tùy chọn,
    nhờ đó node chỉ cần trả về phần state mà nó thực sự thay đổi.

    Thứ tự bồi đắp state bám theo Bước 2 và Bước 3 của `data_flow.md`:
    SourceDataAgent -> RequirementAgent -> DWDesignAgent.
    """

    # --- Đầu vào thô lấy từ PostgreSQL ---
    raw_requirements: list[dict[str, str]]
    raw_data_sources: list[dict[str, str]]

    # --- SourceDataAgent sinh ra ---
    analyzed_schema: SourceSchemaResult

    # --- RequirementAgent sinh ra ---
    analytical_requirements: list[AnalyticalRequirementItem]

    # --- DWDesignAgent sinh ra ---
    proposed_dbml: str
    summary: str

    # --- Trạng thái điều phối của Agent điều phối ---
    validation_error: str
    attempts: int
