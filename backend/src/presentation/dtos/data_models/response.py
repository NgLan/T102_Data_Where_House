"""Response schemas cho API Data Model."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from src.application.data_model_analysis.models import AnalysisDocumentOutput
from src.application.data_models.output import DataModelDdlOutput, DataModelOutput
from src.application.data_warehouse_workflows.output import (
    ValidationIssue,
    ValidationIssueCode,
    ValidationSeverity,
)
from src.domain.data_model.enums import DataModelTargetKind
from src.domain.sandbox.enums import SandboxDbType


class DataModelResponse(BaseModel):
    """Snapshot Data Model trả về cho Frontend editor."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="ID của Data Model")
    project_id: UUID = Field(description="ID dự án sở hữu Data Model")
    dbml: str = Field(min_length=1, description="Snapshot DBML hiện tại")
    revision: int = Field(ge=1, description="Revision phục vụ optimistic locking")
    created_at: datetime = Field(description="Thời điểm tạo theo ISO 8601")
    updated_at: datetime = Field(description="Thời điểm cập nhật theo ISO 8601")
    is_outdated: bool = Field(description="Model không khớp analysis revisions hiện tại")

    @classmethod
    def from_application(cls, output: DataModelOutput) -> "DataModelResponse":
        """Ánh xạ application output sang response DTO."""
        return cls.model_validate(output)


class DataModelValidationIssueResponse(BaseModel):
    """Lỗi hoặc cảnh báo do ValidationEngine phát hiện."""

    model_config = ConfigDict(from_attributes=True)

    code: ValidationIssueCode
    table_name: str
    column_name: str
    severity: ValidationSeverity
    title: str
    description: str

    @classmethod
    def from_application(cls, output: ValidationIssue) -> "DataModelValidationIssueResponse":
        """Ánh xạ application validation issue sang response DTO."""
        return cls.model_validate(output)


class DataModelDdlResponse(BaseModel):
    """DDL sinh từ Data Model hiện hành."""

    model_config = ConfigDict(from_attributes=True)

    ddl: str = Field(description="Script DDL đã sinh")
    db_type: SandboxDbType = Field(description="Database type đích")
    data_model_revision: int = Field(ge=1, description="Revision Data Model nguồn")
    target_kind: DataModelTargetKind
    proposal_change_id: UUID | None = None
    current_revision: int = Field(ge=1)
    base_revision: int = Field(ge=1)

    @classmethod
    def from_application(cls, output: DataModelDdlOutput) -> "DataModelDdlResponse":
        """Ánh xạ application DDL output sang response DTO."""
        return cls.model_validate(output)


class AnalysisDocumentResponse(BaseModel):
    """Tài liệu Markdown và metadata target nguồn."""

    model_config = ConfigDict(from_attributes=True)
    filename: str
    mime_type: str
    content: str
    data_model_revision: int = Field(ge=1)
    target_kind: DataModelTargetKind
    proposal_change_id: UUID | None = None
    current_revision: int = Field(ge=1)
    base_revision: int = Field(ge=1)

    @classmethod
    def from_application(cls, output: AnalysisDocumentOutput) -> "AnalysisDocumentResponse":
        return cls.model_validate(output)
