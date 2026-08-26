"""Giá trị trung gian sau khi parse Requirement Document."""

from dataclasses import dataclass

from src.domain.requirement_file.enums import RequirementFileType


@dataclass(frozen=True, slots=True)
class ParsedRequirementFile:
    """Document đã được kiểm tra và trích xuất text thành công."""

    name: str
    content: bytes
    file_type: RequirementFileType
    extracted_text: str
