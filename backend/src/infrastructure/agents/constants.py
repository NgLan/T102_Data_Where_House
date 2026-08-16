"""Hằng số cấu hình cho hệ thống AI Agent."""

from typing import Final

# Số lần tối đa DWDesignAgent được sinh lại DBML khi ValidationEngine báo sai cú pháp.
# Cố ý đặt thấp hơn nhiều so với `settings.agent_max_iterations` (=10): cả pipeline phải
# trả kết quả dưới 45 giây theo NFR2, retry quá nhiều sẽ phá vỡ ràng buộc đó.
MAX_REVISION_ATTEMPTS: Final[int] = 3

# Tên các node trong đồ thị thiết kế mô hình dữ liệu (pipeline 4 agent).
SOURCE_ANALYSIS_NODE: Final[str] = "source_analysis"
REQUIREMENT_ANALYSIS_NODE: Final[str] = "requirement_analysis"
DESIGN_NODE: Final[str] = "design"
VALIDATE_NODE: Final[str] = "validate"

# Độ dài tối đa của thông điệp lỗi cú pháp gửi ngược lại cho LLM ở lượt retry.
MAX_VALIDATION_ERROR_LENGTH: Final[int] = 500
