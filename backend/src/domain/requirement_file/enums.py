"""Enum cho tài liệu Requirement."""

from enum import StrEnum


class RequirementFileType(StrEnum):
    """Định dạng Requirement Document hỗ trợ trong MVP."""

    DOCX = "DOCX"
    TXT = "TXT"
    MD = "MD"
