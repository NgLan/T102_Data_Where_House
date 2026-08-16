"""Dịch vụ phân tích cấu trúc tệp CSV (.csv)."""

import csv
import io
from datetime import datetime
from typing import Any

from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.data_source.file_parser import ParsedDataSourceResult
from src.domain.data_source.value_objects import (
    ColumnMetadata,
    SchemaMetadata,
    TableMetadata,
)

MAX_PREVIEW_ROWS = 5


class CsvParser:
    """Công cụ đọc và phân tích cấu trúc schema tệp CSV."""

    def parse(self, file_bytes: bytes, filename: str, saved_path: str) -> ParsedDataSourceResult:
        """Đọc tệp CSV, bóc tách cấu trúc cột, kiểu dữ liệu và 5 dòng xem trước.

        Args:
            file_bytes: Dữ liệu nhị phân của tệp CSV.
            filename: Tên tệp gốc.
            saved_path: Đường dẫn lưu trữ tệp trên server.

        Returns:
            ParsedDataSourceResult: Cấu trúc schema và dữ liệu mẫu.
        """
        try:
            text_content = self._decode_bytes(file_bytes)
            return self._extract_csv_data(text_content, filename, saved_path)
        except Exception as exc:
            raise InfrastructureException(
                code=ErrorCode.FILE_PARSING_ERROR,
                message=f"Không thể đọc hoặc phân tích cấu trúc tệp CSV: {filename}",
            ) from exc

    def _decode_bytes(self, file_bytes: bytes) -> str:
        """Giải mã dữ liệu nhị phân sang chuỗi văn bản với cơ chế fallback."""
        try:
            return file_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            try:
                return file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                return file_bytes.decode("latin-1")

    def _extract_csv_data(self, text_content: str, filename: str, saved_path: str) -> ParsedDataSourceResult:
        """Trích xuất dữ liệu và bóc tách các dòng từ nội dung CSV."""
        reader = csv.reader(io.StringIO(text_content))
        header_row = next(reader, None)
        table_name = filename.rsplit(".", 1)[0] if "." in filename else filename

        if not header_row:
            return self._build_empty_result(filename, saved_path, table_name)

        column_names = [str(col).strip() if col else f"Column_{i+1}" for i, col in enumerate(header_row)]
        all_rows: list[list[str]] = [row for row in reader if any(cell.strip() for cell in row)]

        preview_rows = self._build_preview_rows(column_names, all_rows[:MAX_PREVIEW_ROWS])
        columns_meta = self._infer_columns_metadata(column_names, all_rows)
        table_meta = TableMetadata(name=table_name or "Table1", columns=tuple(columns_meta))
        schema_meta = SchemaMetadata(tables=(table_meta,), relationships=())

        return ParsedDataSourceResult(
            name=filename,
            file_path=saved_path,
            file_type="CSV",
            schema_metadata=schema_meta,
            preview_rows=preview_rows,
            total_rows=len(all_rows),
        )

    def _infer_columns_metadata(self, col_names: list[str], data_rows: list[list[str]]) -> list[ColumnMetadata]:
        """Suy luận kiểu dữ liệu và thuộc tính cho danh sách cột."""
        columns: list[ColumnMetadata] = []
        for idx, col_name in enumerate(col_names):
            values = [row[idx].strip() for row in data_rows if idx < len(row) and row[idx].strip() != ""]
            inferred_type = self._infer_single_column_type(values)
            columns.append(
                ColumnMetadata(
                    name=col_name,
                    data_type=inferred_type,
                    nullable=len(values) < len(data_rows),
                )
            )
        return columns

    def _infer_single_column_type(self, values: list[str]) -> str:
        """Xác định kiểu dữ liệu từ danh sách giá trị chuỗi thực tế của một cột."""
        if not values:
            return "TEXT"
        if all(v.lower() in ("true", "false", "1", "0", "t", "f") for v in values):
            return "BOOLEAN"
        if all(self._is_number(v) for v in values):
            return "NUMBER"
        if all(self._is_datetime(v) for v in values):
            return "DATETIME"
        if len(set(values)) <= 5 and len(values) >= 10:
            return "OPTION"
        return "TEXT"

    def _is_number(self, val: str) -> bool:
        """Kiểm tra một chuỗi có phải là số hay không."""
        try:
            float(val.replace(",", ""))
            return True
        except ValueError:
            return False

    def _is_datetime(self, val: str) -> bool:
        """Kiểm tra một chuỗi có phải định dạng ngày giờ hợp lệ hay không."""
        if len(val) < 8 or not any(char in val for char in ("-", "/", ":")):
            return False
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"):
            try:
                datetime.strptime(val, fmt)
                return True
            except ValueError:
                continue
        return False

    def _build_preview_rows(self, col_names: list[str], rows: list[list[str]]) -> list[dict[str, Any]]:
        """Định dạng các dòng preview thành danh sách dict."""
        preview: list[dict[str, Any]] = []
        for row in rows:
            row_dict: dict[str, Any] = {}
            for idx, col in enumerate(col_names):
                row_dict[col] = row[idx] if idx < len(row) else None
            preview.append(row_dict)
        return preview

    def _build_empty_result(self, filename: str, saved_path: str, table_name: str) -> ParsedDataSourceResult:
        """Tạo kết quả rỗng khi tệp CSV không có dữ liệu."""
        table_meta = TableMetadata(name=table_name or "Table1", columns=())
        schema_meta = SchemaMetadata(tables=(table_meta,), relationships=())
        return ParsedDataSourceResult(
            name=filename,
            file_path=saved_path,
            file_type="CSV",
            schema_metadata=schema_meta,
            preview_rows=[],
            total_rows=0,
        )
