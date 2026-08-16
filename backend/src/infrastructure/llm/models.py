"""Schema đầu ra có cấu trúc (Structured Output) mà LLM bắt buộc tuân theo."""

from pydantic import BaseModel, Field


class DbmlRevisionResult(BaseModel):
    """Kết quả LLM trả về khi được yêu cầu chỉnh sửa mô hình dữ liệu DBML.

    Dùng làm schema cho `ChatOpenAI.with_structured_output()` nên mọi mô tả trường ở đây
    đều được gửi kèm cho mô hình — viết bằng tiếng Anh để mô hình bám sát yêu cầu.
    """

    dbml: str = Field(
        description=(
            "The COMPLETE revised DBML document. Must contain every table of the data "
            "model, including tables that were not affected by the request. "
            "Raw DBML only - no markdown fences, no prose, no commentary."
        )
    )
    summary: str = Field(
        description=(
            "One short paragraph in Vietnamese explaining what was changed and why. "
            "This text is shown directly to the user in the chat panel."
        )
    )
    changed_tables: list[str] = Field(
        default_factory=list,
        description="Names of the tables that were added, removed or modified.",
    )
