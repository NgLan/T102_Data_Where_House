"""Thực thể Nguồn dữ liệu (Data Source Entity)."""

from dataclasses import dataclass, field
from uuid import uuid4

from src.domain.data_source.enums import DataSourceType
from src.domain.data_source.rules import validate_data_source_fields
from src.domain.data_source.value_objects import SchemaMetadata
from src.domain.shared.entity import BaseEntity
from src.domain.shared.types import EntityID


@dataclass(eq=False)
class DataSource(BaseEntity):
    """Thực thể đại diện cho Nguồn dữ liệu (Data Source) trong hệ thống."""

    project_id: EntityID = field(default_factory=uuid4)
    name: str = ""
    location: str = ""
    type: DataSourceType = DataSourceType.CSV
    description: str | None = None
    schema_metadata: SchemaMetadata | None = None

    def __post_init__(self) -> None:
        """Thực thi kiểm tra dữ liệu Nguồn dữ liệu."""
        super().__post_init__()
        validate_data_source_fields(self.name, self.location)

    def replace_file(self, location: str, schema_metadata: SchemaMetadata) -> None:
        """Thay nội dung file và metadata sau khi upload lại cùng tên."""
        validate_data_source_fields(self.name, location)
        self.location = location
        self.schema_metadata = schema_metadata
        self.mark_updated()

    def update_column(
        self,
        table_name: str,
        column_name: str,
        data_type: str,
        options: tuple[str, ...],
    ) -> bool:
        """Cập nhật metadata cột, trả về False nếu không tìm thấy."""
        if self.schema_metadata is None:
            return False
        updated = self.schema_metadata.update_column(
            table_name, column_name, data_type, options
        )
        if updated is None:
            return False
        self.schema_metadata = updated
        self.mark_updated()
        return True
