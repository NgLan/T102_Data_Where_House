"""Interface Use Case: Sinh mã DDL từ mô hình dữ liệu DBML (UC5.4 / UC5.5)."""

from abc import ABC, abstractmethod

from src.application.data_models.dto import GenerateDdlInput, GenerateDdlOutput


class IGenerateDdlService(ABC):
    """Interface trừu tượng cho use case sinh mã DDL theo hệ quản trị CSDL đích."""

    @abstractmethod
    async def execute(self, payload: GenerateDdlInput) -> GenerateDdlOutput:
        """Trả về script DDL tương ứng với mô hình dữ liệu và dialect đã chọn."""
        pass
