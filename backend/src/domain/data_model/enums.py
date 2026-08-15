"""Các kiểu liệt kê (Enums) thuộc miền Mô hình Dữ liệu (Data Model)."""

from enum import StrEnum


class DataModelChangeStatus(StrEnum):
    """Trạng thái đề xuất thay đổi mô hình dữ liệu (Data Model Change Status)."""

    PROPOSED = "PROPOSED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CONFLICTED = "CONFLICTED"


class SqlDialect(StrEnum):
    """Hệ quản trị CSDL đích khi sinh mã DDL từ mô hình dữ liệu (UC5.5 / FR1.3)."""

    POSTGRESQL = "postgresql"
    SNOWFLAKE = "snowflake"
    BIGQUERY = "bigquery"
