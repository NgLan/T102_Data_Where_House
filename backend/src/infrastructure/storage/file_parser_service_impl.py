"""Triển khai IFileParserService sử dụng CsvParser và DocxParser."""

from src.domain.data_source.file_parser import (
    IFileParserService,
    ParsedDataSourceResult,
    ParsedRequirementResult,
)
from src.infrastructure.storage.csv_parser import CsvParser
from src.infrastructure.storage.docx_parser import DocxParser


class FileParserServiceImpl(IFileParserService):
    """Hiện thực hóa interface IFileParserService."""

    def __init__(
        self,
        csv_parser: CsvParser | None = None,
        docx_parser: DocxParser | None = None,
    ) -> None:
        """Khởi tạo service với các bộ parser cụ thể."""
        self._csv_parser = csv_parser or CsvParser()
        self._docx_parser = docx_parser or DocxParser()

    def parse_csv(self, file_bytes: bytes, filename: str, saved_path: str) -> ParsedDataSourceResult:
        """Phân tích tệp CSV và trích xuất cấu trúc."""
        return self._csv_parser.parse(file_bytes, filename, saved_path)

    def parse_docx(self, file_bytes: bytes, filename: str, saved_path: str = "") -> ParsedRequirementResult:
        """Phân tích tệp Word và trích xuất văn bản yêu cầu."""
        return self._docx_parser.parse(file_bytes, filename, saved_path)

