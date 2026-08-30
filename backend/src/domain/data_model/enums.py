"""Các kiểu liệt kê (Enums) thuộc miền Mô hình Dữ liệu (Data Model)."""

from enum import StrEnum


class DataModelChangeStatus(StrEnum):
    """Trạng thái đề xuất thay đổi mô hình dữ liệu (Data Model Change Status)."""

    PROPOSED = "PROPOSED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CONFLICTED = "CONFLICTED"


class DataModelTargetKind(StrEnum):
    """Snapshot được một capability đọc mà không thay đổi lifecycle model."""

    CURRENT_MODEL = "CURRENT_MODEL"
    PROPOSAL = "PROPOSAL"
