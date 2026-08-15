"""Hằng số dùng cho quá trình phân tích DBML và sinh mã DDL."""

from typing import Final

# Schema cách ly Sandbox bắt buộc theo FR6.1 (không bao giờ sinh DDL trỏ thẳng vào Production).
DEFAULT_SANDBOX_SCHEMA: Final[str] = "sandbox_dwh"

# Độ dài tối đa cho phép của nội dung DBML đầu vào (chặn payload bất thường).
MAX_DBML_LENGTH: Final[int] = 500_000

# Tiền tố quy ước phân biệt bảng Dimension và bảng Fact theo chuẩn Kimball.
DIMENSION_TABLE_PREFIX: Final[str] = "dim_"
FACT_TABLE_PREFIX: Final[str] = "fact_"

# Các từ khóa mở đầu khối trong DBML mà bộ sinh DDL bỏ qua có kiểm soát.
IGNORED_BLOCK_KEYWORDS: Final[frozenset[str]] = frozenset(
    {"project", "note", "tablegroup", "tablepartial"}
)

# Ký hiệu quan hệ hợp lệ trong khai báo `Ref`.
RELATIONSHIP_OPERATORS: Final[frozenset[str]] = frozenset({">", "<", "-", "<>"})

# Kiểu dữ liệu mặc định khi không xác định được ánh xạ.
FALLBACK_COLUMN_TYPE: Final[str] = "TEXT"

# Độ dài mặc định gán cho kiểu chuỗi khi DBML không khai báo tham số.
DEFAULT_VARCHAR_LENGTH: Final[int] = 255
