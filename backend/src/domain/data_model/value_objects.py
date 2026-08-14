"""Các value object phục vụ phân tích DBML."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ColumnDefinition:
    """Định nghĩa một cột được đọc từ DBML."""

    name: str
    data_type: str
    primary_key: bool = False
    nullable: bool = True
    increment: bool = False
    reference: str | None = None


@dataclass(frozen=True, slots=True)
class TableDefinition:
    """Định nghĩa một bảng được đọc từ DBML."""

    name: str
    columns: tuple[ColumnDefinition, ...]
