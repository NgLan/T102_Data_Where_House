"""State schema dùng chung cho các đồ thị LangGraph của hệ thống AI Agent."""

from __future__ import annotations

from typing import TypedDict


class DwDesignState(TypedDict, total=False):
    """State của đồ thị chỉnh sửa mô hình dữ liệu (DWDesignAgent).

    Mỗi node đọc và ghi vào state này. `total=False` cho phép mọi trường là tùy chọn,
    nhờ đó node chỉ cần trả về phần state mà nó thực sự thay đổi.
    """

    # --- Đầu vào ---
    current_dbml: str
    instruction: str

    # --- Kết quả do DWDesignAgent sinh ra ---
    proposed_dbml: str
    summary: str
    changed_tables: list[str]

    # --- Trạng thái điều phối ---
    validation_error: str
    attempts: int
