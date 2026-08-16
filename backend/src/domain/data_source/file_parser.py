"""Interface và DTO cho dịch vụ phân tích tệp tin nguồn (File Parser Service)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from src.domain.data_source.value_objects import SchemaMetadata


@dataclass(frozen=True)
class ParsedDataSourceResult:
    """Kết quả phân tích từ tệp tin dữ liệu nguồn (VD: .csv)."""

    name: str
    file_path: str
    file_type: str
    schema_metadata: SchemaMetadata
    preview_rows: list[dict[str, Any]] = field(default_factory=list)
    total_rows: int = 0


@dataclass(frozen=True)
class ParsedRequirementResult:
    """Kết quả phân tích từ tệp tin yêu cầu nghiệp vụ (VD: .docx)."""

    name: str
    file_path: str
    content: str


class IFileParserService(ABC):
    """Interface định nghĩa hợp đồng bóc tách dữ liệu từ tệp tin."""

    @abstractmethod
    def parse_csv(self, file_bytes: bytes, filename: str, saved_path: str) -> ParsedDataSourceResult:
        """Bóc tách cấu trúc cột, kiểu dữ liệu và 5 dòng preview từ tệp CSV.

        Args:
            file_bytes: Dữ liệu nhị phân của tệp.
            filename: Tên tệp gốc.
            saved_path: Đường dẫn lưu trữ tệp vật lý.

        Returns:
            ParsedDataSourceResult: Dữ liệu bóc tách được.
        """
        pass

    @abstractmethod
    def parse_docx(self, file_bytes: bytes, filename: str, saved_path: str = "") -> ParsedRequirementResult:
        """Bóc tách nội dung văn bản từ tệp Word (.docx) trực tiếp từ bộ nhớ.

        Args:
            file_bytes: Dữ liệu nhị phân của tệp.
            filename: Tên tệp gốc.
            saved_path: Đường dẫn lưu trữ tệp vật lý (mặc định là rỗng).

        Returns:
            ParsedRequirementResult: Nội dung văn bản bóc tách được.
        """
        pass

