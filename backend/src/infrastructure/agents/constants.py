"""Hằng số cấu hình cho hệ thống AI Agent."""

from typing import Final

# Số lần tối đa DWDesignAgent được sinh lại DBML khi ValidationEngine báo sai cú pháp.
# Cố ý đặt thấp hơn nhiều so với `settings.agent_max_iterations` (=10): một lượt chỉnh sửa
# phải trả kết quả dưới 15 giây theo NFR2, retry quá nhiều sẽ phá vỡ ràng buộc đó.
MAX_REVISION_ATTEMPTS: Final[int] = 3

# Tên các node trong đồ thị thiết kế mô hình dữ liệu.
DESIGN_NODE: Final[str] = "design"
VALIDATE_NODE: Final[str] = "validate"

# Độ dài tối đa của thông điệp lỗi cú pháp gửi ngược lại cho LLM ở lượt retry.
MAX_VALIDATION_ERROR_LENGTH: Final[int] = 500
