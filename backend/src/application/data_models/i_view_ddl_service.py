"""Interface của use case xem mã DDL."""

from typing import Protocol

from src.domain.data_model.entities import DataModelSnapshot, DdlDocument
from src.domain.data_model.enums import DdlDialect


class IViewDdlService(Protocol):
    """Hợp đồng sinh DDL từ một ảnh chụp mô hình."""

    def execute(self, model: DataModelSnapshot, dialect: DdlDialect) -> DdlDocument:
        """Sinh tài liệu DDL theo dialect được yêu cầu."""
        ...
