"""Cổng (Port) sinh mô hình dữ liệu bằng AI thuộc miền Mô hình Dữ liệu (T-019)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.data_source.entities import DataSource
from src.domain.data_source.value_objects import SchemaMetadata
from src.domain.requirement.entities import Requirement


@dataclass(frozen=True)
class DbmlGenerationResult:
    """Kết quả pipeline AI sinh mô hình kho dữ liệu từ yêu cầu và nguồn dữ liệu."""

    dbml: str
    summary: str
    analyzed_schema: SchemaMetadata
    analytical_requirements: tuple[AnalyticalRequirement, ...] = field(default_factory=tuple)
    attempts: int = 1


class IDataModelGenerator(ABC):
    """Interface trừu tượng cho pipeline AI sinh mô hình dữ liệu lần đầu.

    Tầng Application chỉ phụ thuộc vào interface này, không biết gì về LangGraph hay
    nhà cung cấp LLM cụ thể đang dùng ở tầng Infrastructure.
    """

    @abstractmethod
    async def generate(
        self,
        requirements: list[Requirement],
        data_sources: list[DataSource],
    ) -> DbmlGenerationResult:
        """Chạy pipeline 4 agent để sinh mô hình DBML từ yêu cầu và nguồn dữ liệu."""
        pass
