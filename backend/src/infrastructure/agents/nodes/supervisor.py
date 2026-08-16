"""Node Agent điều phối: kiểm định DBML và quyết định có sinh lại hay không.

Tương ứng thành phần **Agent điều phối** và **ValidationEngine** ở Bước 4 của
`docs/guide_cho_ca_nhom/data_flow.md`: DBML sai cú pháp thì quay lại DWDesignAgent (retry),
hợp lệ thì kết thúc luồng.
"""

from langgraph.graph import END
from src.common.exceptions.business import BusinessException
from src.common.logging import get_logger
from src.common.utils.string import truncate
from src.infrastructure.agents.constants import (
    DESIGN_NODE,
    MAX_REVISION_ATTEMPTS,
    MAX_VALIDATION_ERROR_LENGTH,
)
from src.infrastructure.agents.state import DwDesignState
from src.infrastructure.codegen.dbml_parser import parse_dbml
from src.infrastructure.security.pii_guard import PiiGuard

logger = get_logger(__name__)

_RESIDUAL_PII_ERROR = (
    "DBML còn sót mã ẩn danh PII (dạng `pii_field_NN`). Bạn đã đổi tên các mã này — "
    "hãy giữ nguyên chúng y hệt như trong mô hình đầu vào."
)


def build_validate_node(pii_guard: PiiGuard):
    """Tạo node kiểm định gắn với bộ che PII đang dùng."""

    async def validate_node(state: DwDesignState) -> DwDesignState:
        """Kiểm định DBML: trước hết soát mã ẩn danh còn sót, sau đó kiểm tra cú pháp."""
        proposed_dbml = state.get("proposed_dbml", "")
        attempts = state.get("attempts", 0)

        # Chốt chặn fail-closed: hoàn nguyên PII không trọn vẹn thì coi như lượt sinh hỏng,
        # tuyệt đối không để DBML mang tên cột giả lọt vào Data Model chính thức.
        if pii_guard.has_residual_placeholder(proposed_dbml):
            logger.warning("pii_unmask_incomplete attempt=%d", attempts)
            return {"validation_error": _RESIDUAL_PII_ERROR}

        try:
            parse_dbml(proposed_dbml)
        except BusinessException as exc:
            logger.warning(
                "dbml_validation_failed attempt=%d error=%s",
                attempts,
                exc.message,
            )
            return {"validation_error": truncate(exc.message, MAX_VALIDATION_ERROR_LENGTH)}

        logger.info("dbml_validation_passed attempt=%d", attempts)
        return {"validation_error": ""}

    return validate_node


def should_retry(state: DwDesignState) -> str:
    """Quyết định tuyến đi tiếp: sinh lại DBML hay kết thúc đồ thị."""
    if not state.get("validation_error"):
        return END

    if state.get("attempts", 0) >= MAX_REVISION_ATTEMPTS:
        logger.error(
            "dbml_revision_exhausted attempts=%d", state.get("attempts", 0)
        )
        return END

    return DESIGN_NODE
