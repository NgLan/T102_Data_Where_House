"""Cổng (Port) sinh mã DDL từ mô hình dữ liệu DBML thuộc miền Mô hình Dữ liệu."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from src.domain.data_model.enums import SqlDialect


@dataclass(frozen=True)
class DdlGenerationResult:
    """Kết quả sinh mã DDL từ nội dung DBML."""

    ddl: str
    dialect: SqlDialect
    schema_name: str
    table_count: int
    warnings: list[str] = field(default_factory=list)


class IDdlGenerator(ABC):
    """Interface trừu tượng cho bộ sinh mã DDL từ nội dung DBML."""

    @abstractmethod
    def generate(
        self,
        dbml: str,
        dialect: SqlDialect,
        schema_name: str | None = None,
    ) -> DdlGenerationResult:
        """Biên dịch nội dung DBML thành script DDL của hệ quản trị CSDL đích."""
        pass
