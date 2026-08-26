"""Thực thể Nguồn dữ liệu (Data Source Entity)."""

from dataclasses import dataclass

from src.common.exceptions.error_codes import ErrorCode
from src.common.utils.string import safe_strip
from src.domain.data_source.enums import DataSourceType
from src.domain.data_source.rules import normalize_data_source_fields
from src.domain.data_source.semantic_metadata import SourceSemanticAnnotation
from src.domain.data_source.value_objects import ColumnUpdate, SchemaMetadata
from src.domain.shared.entity import BaseEntity
from src.domain.shared.enum_rules import normalize_str_enum
from src.domain.shared.types import EntityID


@dataclass(eq=False, kw_only=True)
class DataSource(BaseEntity):
    """Thực thể đại diện cho Nguồn dữ liệu (Data Source) trong hệ thống."""

    project_id: EntityID
    name: str
    location: str
    type: DataSourceType = DataSourceType.CSV
    description: str | None = None
    schema_metadata: SchemaMetadata | None = None

    def __post_init__(self) -> None:
        """Thực thi kiểm tra dữ liệu Nguồn dữ liệu."""
        super().__post_init__()
        self.name, self.location = normalize_data_source_fields(self.name, self.location)
        self.type = normalize_str_enum(self.type, DataSourceType, ErrorCode.VALIDATION_ERROR)
        self.description = safe_strip(self.description)

    def replace_file(
        self,
        location: str,
        schema_metadata: SchemaMetadata | None,
    ) -> None:
        """Thay nội dung file và metadata sau khi upload lại cùng tên.

        Args:
            location: Vị trí lưu file mới.
            schema_metadata: Schema đã phân tích hoặc ``None`` khi chờ Analyze.

        Raises:
            BusinessException: Khi location không hợp lệ.

        Side Effects:
            Thay snapshot schema và cập nhật ``updated_at``.
        """
        _, normalized_location = normalize_data_source_fields(self.name, location)
        self.location = normalized_location
        self.schema_metadata = schema_metadata
        self.mark_updated()

    def update_column(self, update: ColumnUpdate) -> bool:
        """Cập nhật metadata cột theo value object.

        Args:
            update: Thay đổi cột đã được chuẩn hóa.

        Returns:
            ``True`` nếu tìm thấy cột và cập nhật; ngược lại ``False``.

        Side Effects:
            Thay snapshot schema và cập nhật ``updated_at`` khi thành công.
        """
        if self.schema_metadata is None:
            return False
        updated = self.schema_metadata.update_column(update)
        if updated is None:
            return False
        self.schema_metadata = updated
        self.mark_updated()
        return True

    def annotate_column(
        self,
        table_name: str,
        column_name: str,
        annotation: SourceSemanticAnnotation,
    ) -> bool:
        """Áp dụng semantic decision lên column hiện hữu."""
        if self.schema_metadata is None:
            return False
        updated = self.schema_metadata.annotate_column(table_name, column_name, annotation)
        return self._replace_annotated_schema(updated)

    def annotate_relationship(
        self,
        from_column: str,
        to_column: str,
        annotation: SourceSemanticAnnotation,
    ) -> bool:
        """Áp dụng semantic decision lên relationship hiện hữu."""
        if self.schema_metadata is None:
            return False
        updated = self.schema_metadata.annotate_relationship(
            from_column, to_column, annotation
        )
        return self._replace_annotated_schema(updated)

    def _replace_annotated_schema(self, updated: SchemaMetadata | None) -> bool:
        if updated is None:
            return False
        self.schema_metadata = updated
        self.mark_updated()
        return True

    def remove_user_annotation(
        self, requirement_id: EntityID, concept_key: str
    ) -> None:
        """Xóa scoped USER semantic decision khỏi source hiện hành."""
        if self.schema_metadata is None:
            return
        self.schema_metadata = self.schema_metadata.remove_user_annotation(
            requirement_id, concept_key
        )
        self.mark_updated()
