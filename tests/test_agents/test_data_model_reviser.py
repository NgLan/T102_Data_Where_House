"""Kiểm thử đồ thị LangGraph chỉnh sửa mô hình dữ liệu (T-024).

Toàn bộ bài kiểm thử dùng Chat Model giả lập — KHÔNG gọi LLM thật, không tốn chi phí API.
"""

from typing import Any

import pytest
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.infrastructure.agents.constants import MAX_REVISION_ATTEMPTS
from src.infrastructure.agents.data_model_reviser import LangGraphDataModelReviser
from src.infrastructure.llm.models import DbmlRevisionResult
from src.infrastructure.security.pii_guard import PiiGuard

CURRENT_DBML = """Table Dim_Driver {
  driver_key int [pk]
  full_name varchar(100)
  vehicle_type varchar(30)
}"""

VALID_REVISED_DBML = """Table Dim_Driver {
  driver_key int [pk]
  full_name varchar(100)
  vehicle_key int [ref: > Dim_Vehicle.vehicle_key]
}

Table Dim_Vehicle {
  vehicle_key int [pk]
  vehicle_type varchar(30)
}"""

INVALID_DBML = "Table Dim_Driver { driver_key"


class FakeStructuredModel:
    """Runnable giả lập kết quả `with_structured_output()`, trả lần lượt các kịch bản."""

    def __init__(self, results: list[DbmlRevisionResult]) -> None:
        """Khởi tạo với danh sách kết quả trả về theo từng lượt gọi."""
        self._results = results
        self.call_count = 0
        self.received_prompts: list[str] = []

    async def ainvoke(self, messages: Any, *args: Any, **kwargs: Any) -> DbmlRevisionResult:
        """Trả kết quả kế tiếp và ghi lại nội dung prompt nhận được."""
        self.received_prompts.append(str(messages[-1].content))
        index = min(self.call_count, len(self._results) - 1)
        self.call_count += 1
        return self._results[index]


class FakeChatModel:
    """Chat Model giả lập, chỉ cần đáp ứng `with_structured_output()`."""

    def __init__(self, results: list[DbmlRevisionResult]) -> None:
        """Khởi tạo cùng danh sách kết quả kịch bản."""
        self.structured = FakeStructuredModel(results)

    def with_structured_output(self, schema: Any, **kwargs: Any) -> FakeStructuredModel:
        """Trả về runnable giả lập."""
        return self.structured


def _result(dbml: str, summary: str = "Đã tách bảng.") -> DbmlRevisionResult:
    """Tạo nhanh một kết quả LLM giả lập."""
    return DbmlRevisionResult(dbml=dbml, summary=summary, changed_tables=["Dim_Driver"])


def _build_reviser(
    results: list[DbmlRevisionResult], pii_enabled: bool = False
) -> tuple[LangGraphDataModelReviser, FakeChatModel]:
    """Dựng bộ chỉnh sửa cùng Chat Model giả lập.

    Mặc định TẮT che PII để các bài kiểm thử về vòng lặp retry không bị nhiễu; các bài
    kiểm thử riêng về PII sẽ bật lại.
    """
    chat_model = FakeChatModel(results)
    reviser = LangGraphDataModelReviser(chat_model, PiiGuard(enabled=pii_enabled))
    return reviser, chat_model


@pytest.mark.asyncio
async def test_revise_returns_proposal_when_dbml_is_valid() -> None:
    """DBML hợp lệ ngay lần đầu thì trả kết quả và chỉ gọi LLM đúng một lần."""
    reviser, chat_model = _build_reviser([_result(VALID_REVISED_DBML)])

    proposal = await reviser.revise(CURRENT_DBML, "tách Dim_Driver thành Dim_Driver và Dim_Vehicle")

    assert proposal.dbml == VALID_REVISED_DBML
    assert proposal.summary == "Đã tách bảng."
    assert proposal.changed_tables == ["Dim_Driver"]
    assert proposal.attempts == 1
    assert chat_model.structured.call_count == 1


@pytest.mark.asyncio
async def test_revise_retries_when_first_attempt_has_invalid_syntax() -> None:
    """DBML sai cú pháp ở lượt đầu phải được sinh lại và lượt hai hợp lệ thì chấp nhận."""
    reviser, chat_model = _build_reviser([_result(INVALID_DBML), _result(VALID_REVISED_DBML)])

    proposal = await reviser.revise(CURRENT_DBML, "tách bảng")

    assert proposal.dbml == VALID_REVISED_DBML
    assert proposal.attempts == 2
    assert chat_model.structured.call_count == 2


@pytest.mark.asyncio
async def test_retry_prompt_contains_validation_error() -> None:
    """Lượt retry phải gửi kèm thông điệp lỗi cú pháp để LLM biết đường sửa."""
    reviser, chat_model = _build_reviser([_result(INVALID_DBML), _result(VALID_REVISED_DBML)])

    await reviser.revise(CURRENT_DBML, "tách bảng")

    retry_prompt = chat_model.structured.received_prompts[1]
    assert "KHÔNG hợp lệ" in retry_prompt
    assert "sinh lại toàn bộ DBML" in retry_prompt.lower() or "sinh lại" in retry_prompt


@pytest.mark.asyncio
async def test_revise_raises_after_exhausting_all_attempts() -> None:
    """Sai cú pháp ở mọi lượt thì dừng đúng số lần cho phép và ném lỗi nghiệp vụ."""
    reviser, chat_model = _build_reviser([_result(INVALID_DBML)])

    with pytest.raises(BusinessException) as exc_info:
        await reviser.revise(CURRENT_DBML, "tách bảng")

    assert exc_info.value.code == ErrorCode.INVALID_DBML_CONTENT
    assert chat_model.structured.call_count == MAX_REVISION_ATTEMPTS


@pytest.mark.asyncio
async def test_first_prompt_contains_current_dbml_and_instruction() -> None:
    """Prompt lượt đầu phải chứa đủ DBML hiện tại và yêu cầu của người dùng."""
    reviser, chat_model = _build_reviser([_result(VALID_REVISED_DBML)])

    await reviser.revise(CURRENT_DBML, "thêm cột rating vào Dim_Driver")

    first_prompt = chat_model.structured.received_prompts[0]
    assert "Dim_Driver" in first_prompt
    assert "thêm cột rating vào Dim_Driver" in first_prompt


# --- PII Guard (FR6.2) --------------------------------------------------------

PII_DBML = """Table Dim_Customer {
  customer_key int [pk]
  phone_number varchar(20)
  member_tier varchar(20)
}"""

MASKED_DBML_FROM_LLM = """Table Dim_Customer {
  customer_key int [pk]
  pii_field_01 varchar(20)
  member_tier varchar(20)
  loyalty_point int
}"""


@pytest.mark.asyncio
async def test_sensitive_column_is_masked_before_reaching_llm() -> None:
    """Tên cột nhạy cảm không được xuất hiện trong prompt gửi lên LLM (FR6.2)."""
    reviser, chat_model = _build_reviser([_result(MASKED_DBML_FROM_LLM)], pii_enabled=True)

    await reviser.revise(PII_DBML, "thêm cột loyalty_point")

    first_prompt = chat_model.structured.received_prompts[0]
    assert "phone_number" not in first_prompt
    assert "pii_field_01" in first_prompt
    # Cột nghiệp vụ bình thường vẫn phải giữ nguyên để AI hiểu ngữ cảnh
    assert "member_tier" in first_prompt


@pytest.mark.asyncio
async def test_pii_value_in_instruction_is_masked_before_reaching_llm() -> None:
    """Giá trị PII người dùng gõ trong câu lệnh cũng bị che trước khi gửi đi."""
    reviser, chat_model = _build_reviser([_result(MASKED_DBML_FROM_LLM)], pii_enabled=True)

    await reviser.revise(PII_DBML, "thêm cột liên hệ, ví dụ 0901234567 và a@b.com")

    first_prompt = chat_model.structured.received_prompts[0]
    assert "0901234567" not in first_prompt
    assert "a@b.com" not in first_prompt
    assert "[PII_PHONE]" in first_prompt
    assert "[PII_EMAIL]" in first_prompt


@pytest.mark.asyncio
async def test_masked_column_is_restored_in_final_proposal() -> None:
    """Kết quả trả về người dùng phải mang lại tên cột gốc, không còn mã ẩn danh."""
    reviser, _ = _build_reviser([_result(MASKED_DBML_FROM_LLM)], pii_enabled=True)

    proposal = await reviser.revise(PII_DBML, "thêm cột loyalty_point")

    assert "phone_number" in proposal.dbml
    assert "pii_field_01" not in proposal.dbml
    assert "loyalty_point" in proposal.dbml


@pytest.mark.asyncio
async def test_summary_is_unmasked_for_display() -> None:
    """Lời giải thích hiển thị cho người dùng cũng phải hoàn nguyên tên cột gốc."""
    result = _result(MASKED_DBML_FROM_LLM, summary="Đã giữ nguyên cột pii_field_01.")
    reviser, _ = _build_reviser([result], pii_enabled=True)

    proposal = await reviser.revise(PII_DBML, "thêm cột loyalty_point")

    assert "phone_number" in proposal.summary
    assert "pii_field_01" not in proposal.summary


@pytest.mark.asyncio
async def test_renamed_placeholder_triggers_retry_then_fails_closed() -> None:
    """LLM tự đổi mã ẩn danh thì hoàn nguyên hụt, phải retry rồi từ chối lưu đề xuất.

    Đây là chốt chặn quan trọng nhất của PII Guard: tuyệt đối không để DBML mang tên cột
    giả (`pii_field_1`) lọt vào Data Model chính thức.
    """
    corrupted = MASKED_DBML_FROM_LLM.replace("pii_field_01", "pii_field_1")
    reviser, chat_model = _build_reviser([_result(corrupted)], pii_enabled=True)

    with pytest.raises(BusinessException) as exc_info:
        await reviser.revise(PII_DBML, "thêm cột loyalty_point")

    assert exc_info.value.code == ErrorCode.INVALID_DBML_CONTENT
    assert chat_model.structured.call_count == MAX_REVISION_ATTEMPTS


@pytest.mark.asyncio
async def test_retry_prompt_tells_llm_to_keep_placeholder_intact() -> None:
    """Lượt retry phải nói rõ cho LLM biết lý do là do đổi mã ẩn danh."""
    corrupted = MASKED_DBML_FROM_LLM.replace("pii_field_01", "pii_field_1")
    reviser, chat_model = _build_reviser(
        [_result(corrupted), _result(MASKED_DBML_FROM_LLM)], pii_enabled=True
    )

    await reviser.revise(PII_DBML, "thêm cột loyalty_point")

    retry_prompt = chat_model.structured.received_prompts[1]
    assert "pii_field_NN" in retry_prompt


@pytest.mark.asyncio
async def test_disabled_guard_sends_original_column_names() -> None:
    """Tắt cấu hình thì dữ liệu đi thẳng, dùng để gỡ lỗi chất lượng đầu ra của Agent."""
    passthrough = PII_DBML.replace("member_tier varchar(20)", "member_tier varchar(20)\n  loyalty_point int")
    reviser, chat_model = _build_reviser([_result(passthrough)], pii_enabled=False)

    proposal = await reviser.revise(PII_DBML, "thêm cột loyalty_point")

    assert "phone_number" in chat_model.structured.received_prompts[0]
    assert "phone_number" in proposal.dbml
