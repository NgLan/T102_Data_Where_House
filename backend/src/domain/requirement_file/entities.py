"""Domain entity cho Requirement Document."""

from dataclasses import dataclass

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.requirement_file.enums import RequirementFileType
from src.domain.shared.entity import BaseEntity
from src.domain.shared.enum_rules import normalize_str_enum
from src.domain.shared.types import EntityID


@dataclass(eq=False, kw_only=True)
class RequirementFile(BaseEntity):
    """Tài liệu làm context cho RequirementAgent."""

    project_id: EntityID
    name: str
    location: str
    extracted_text: str
    file_type: RequirementFileType

    def __post_init__(self) -> None:
        """Chuẩn hóa và bảo vệ content bắt buộc."""
        super().__post_init__()
        self.name = self.name.strip()
        self.location = self.location.strip()
        self.extracted_text = self.extracted_text.strip()
        self.file_type = normalize_str_enum(
            self.file_type, RequirementFileType, ErrorCode.VALIDATION_ERROR
        )
        if not self.name or not self.location or not self.extracted_text:
            raise BusinessException(
                ErrorCode.VALIDATION_ERROR,
                "Requirement Document phải có tên, location và extracted text.",
            )

    def replace(self, location: str, extracted_text: str) -> bool:
        """Thay file và trả về việc Agent context có thực sự đổi hay không."""
        normalized_location = location.strip()
        normalized_text = extracted_text.strip()
        if not normalized_location or not normalized_text:
            raise BusinessException(
                ErrorCode.VALIDATION_ERROR,
                "Requirement Document không được rỗng.",
            )
        is_changed = self.extracted_text != normalized_text
        self.location = normalized_location
        self.extracted_text = normalized_text
        self.mark_updated()
        return is_changed
