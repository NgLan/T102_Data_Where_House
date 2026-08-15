"""Cấu trúc cây cú pháp trung gian (AST) biểu diễn nội dung DBML đã phân tích."""

from dataclasses import dataclass, field


@dataclass
class ParsedColumn:
    """Một cột trong bảng DBML sau khi phân tích cú pháp."""

    name: str
    raw_type: str
    is_primary_key: bool = False
    is_not_null: bool = False
    is_unique: bool = False
    is_increment: bool = False
    default_value: str | None = None
    note: str | None = None


@dataclass
class ParsedRef:
    """Một quan hệ khóa ngoại giữa hai bảng trong DBML."""

    from_table: str
    from_column: str
    to_table: str
    to_column: str


@dataclass
class ParsedIndex:
    """Một chỉ mục (index) được khai báo trong khối `indexes` của bảng DBML."""

    columns: list[str]
    is_unique: bool = False
    name: str | None = None


@dataclass
class ParsedTable:
    """Một bảng trong DBML sau khi phân tích cú pháp."""

    name: str
    columns: list[ParsedColumn] = field(default_factory=list)
    indexes: list[ParsedIndex] = field(default_factory=list)
    note: str | None = None

    @property
    def primary_key_columns(self) -> list[str]:
        """Danh sách tên cột được đánh dấu là khóa chính."""
        return [column.name for column in self.columns if column.is_primary_key]


@dataclass
class ParsedEnum:
    """Một kiểu liệt kê (Enum) được khai báo trong DBML."""

    name: str
    values: list[str] = field(default_factory=list)


@dataclass
class ParsedSchema:
    """Toàn bộ mô hình dữ liệu DBML sau khi phân tích cú pháp."""

    tables: list[ParsedTable] = field(default_factory=list)
    refs: list[ParsedRef] = field(default_factory=list)
    enums: list[ParsedEnum] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def enum_names(self) -> set[str]:
        """Tập hợp tên các Enum đã khai báo (dùng để ánh xạ kiểu dữ liệu)."""
        return {enum.name for enum in self.enums}
