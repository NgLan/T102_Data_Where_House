from typing import Any, Literal

from pydantic import BaseModel, Field

# --- JSON Schema Core Data Structures for AI Agent Pipeline ---


class TableColumn(BaseModel):
    name: str = Field(..., description="Tên cột (snake_case)")
    data_type: str = Field(
        ..., description="Kiểu dữ liệu BigQuery (STRING, INT64, NUMERIC, TIMESTAMP, DATE, BOOL, STRUCT, ARRAY)"
    )
    nullable: bool = Field(default=True, description="Cột có thể NULL hay không")
    is_pii_masked: bool = Field(default=False, description="Cột đã được che thông tin cá nhân (PII Masked)")
    description: str = Field(..., description="Mô tả ý nghĩa của cột dữ liệu")


class ForeignKeyRelation(BaseModel):
    column_name: str = Field(..., description="Tên cột ngoại trong bảng hiện tại")
    referenced_table: str = Field(..., description="Tên bảng được tham chiếu")
    referenced_column: str = Field(..., description="Tên cột được tham chiếu trong bảng đích")


class TableDefinition(BaseModel):
    table_name: str = Field(..., description="Tên bảng (ví dụ: dim_customers, fact_orders)")
    table_type: Literal["Fact", "Dimension", "Bridge", "Aggregate"] = Field(
        ..., description="Phân loại bảng theo kiến trúc Kimball: Fact, Dimension, Bridge hoặc Aggregate"
    )
    grain: str = Field(..., description="Mô tả chi tiết độ mịn dữ liệu (Grain)")
    primary_key: list[str] = Field(default_factory=list, description="Danh sách các cột đóng vai trò Primary Key")
    foreign_keys: list[ForeignKeyRelation] = Field(
        default_factory=list, description="Danh sách các mối quan hệ Foreign Key"
    )
    partition_by: str | None = Field(
        default=None, description="Trường partitioning trong BigQuery (ví dụ: DATE(order_timestamp))"
    )
    cluster_by: list[str] = Field(default_factory=list, description="Danh sách tối đa 4 cột clustering trong BigQuery")
    columns: list[TableColumn] = Field(..., description="Danh sách các cột trong bảng")
    ddl_sql: str = Field(
        ..., description="Câu lệnh Google BigQuery Standard SQL DDL (CREATE OR REPLACE TABLE sandbox_schema....)"
    )


class AntiPatternWarning(BaseModel):
    code: str = Field(..., description="Mã cảnh báo anti-pattern (ví dụ: WARN_BQ_MISSING_PARTITION, CRIT_FAN_TRAP)")
    severity: Literal["CRITICAL", "WARNING", "INFO"] = Field(..., description="Mức độ nghiêm trọng")
    target: str = Field(..., description="Tên bảng hoặc cột bị ảnh hưởng")
    message: str = Field(..., description="Nội dung cảnh báo chi tiết")
    recommendation: str = Field(..., description="Khuyến nghị cách khắc phục")


class ModelMetadata(BaseModel):
    domain: str = Field(..., description="Tên miền bài toán nghiệp vụ")
    dialect: str = Field(default="bigquery", description="SQL Dialect (mặc định bigquery)")
    summary: str = Field(..., description="Tóm tắt tổng quan về thiết kế kiến trúc data schema")
    quality_score: int = Field(default=90, ge=0, le=100, description="Điểm chất lượng thiết kế từ Critic Agent")


class DataModelSchema(BaseModel):
    model_metadata: ModelMetadata = Field(..., description="Thông tin metadata tổng quan")
    tables: list[TableDefinition] = Field(..., description="Danh sách các bảng Fact và Dimension")
    anti_pattern_warnings: list[AntiPatternWarning] = Field(
        default_factory=list, description="Danh sách cảnh báo bẫy thiết kế (Anti-patterns)"
    )


class SandboxExecutionPlan(BaseModel):
    sandbox_schema_prefix: str = Field(default="sandbox_schema", description="Tiền tố bảo mật cách ly cho Sandbox DB")
    dry_run_status: str = Field(default="SUCCESS", description="Trạng thái thực thi DDL trên Sandbox DB")
    execution_logs: list[str] = Field(default_factory=list, description="Log trả về từ Sandbox Database (Bước 8)")


class UploadedTableInput(BaseModel):
    table_name: str = Field(..., description="Tên bảng nạp vào (tối đa 20 bảng)")
    raw_schema_ddl: str | None = Field(default=None, description="Chuỗi DDL SQL hoặc JSON schema thô")
    columns_sample: list[str] = Field(default_factory=list, description="Mẫu tên các cột trong bảng")


# --- API Request & Response DTOs ---


class GenerateSchemaRequest(BaseModel):
    project_id: str = Field(default="analytics-prod-2026", description="Google Cloud Project ID")
    dataset_id: str = Field(default="ecommerce_dw", description="BigQuery Dataset ID")
    business_requirements: str = Field(..., min_length=10, max_length=15000, description="Mô tả nghiệp vụ (< 3000 từ)")
    uploaded_tables: list[UploadedTableInput] = Field(
        default_factory=list, max_length=20, description="Tải lên tối đa 20 bảng dữ liệu (Bước 1 Input)"
    )
    sql_dialect: Literal["bigquery", "postgresql", "snowflake", "mysql", "sqlite"] = Field(
        default="bigquery", description="SQL Dialect target"
    )
    enable_pii_masking: bool = Field(default=True, description="Kích hoạt Security Module PII Masking (Bước 2)")
    enable_rag_context: bool = Field(default=True, description="Kích hoạt RAG Knowledge Base Kimball rules (Bước 3)")
    hitl_refinement_comments: str | None = Field(
        default=None, description="Ghi chú phản hồi tinh chỉnh từ HITL Dashboard (Bước 6)"
    )


class SchemaGenerationData(BaseModel):
    schema_id: str = Field(..., description="ID duy nhất của Schema được khởi tạo")
    created_at: str = Field(..., description="Thời điểm khởi tạo ISO format")
    pii_masked: bool = Field(default=True, description="Trạng thái đã quét bảo mật Security Module")
    rag_context_applied: bool = Field(default=True, description="Trạng thái đã áp dụng RAG Knowledge Base")
    model_metadata: ModelMetadata
    tables: list[TableDefinition]
    mermaid_erd: str = Field(..., description="Cấu trúc sơ đồ thực thể ERD Mermaid.js cho Interactive Canvas (Bước 5)")
    sandbox_execution_plan: SandboxExecutionPlan = Field(..., description="Kế hoạch thực thi Sandbox DB (Bước 7 & 8)")
    anti_pattern_warnings: list[AntiPatternWarning] = Field(
        default_factory=list, description="Danh sách cảnh báo bẫy thiết kế từ Critic Agent"
    )


class GenerateSchemaResponse(BaseModel):
    status: str = Field(default="success", description="Trạng thái phản hồi ('success' hoặc 'error')")
    code: int = Field(default=200, description="HTTP Status Code")
    message: str = Field(
        default="Schema generated successfully through 8-step AI pipeline", description="Thông điệp phản hồi"
    )
    data: SchemaGenerationData | None = Field(default=None, description="Dữ liệu Data Model Schema")
    error: dict[str, Any] | None = Field(default=None, description="Chi tiết lỗi nếu có")


class ValidateSchemaRequest(BaseModel):
    ddl_sql_content: str = Field(..., min_length=5, description="Nội dung DDL SQL cần thẩm định")
    sql_dialect: Literal["bigquery", "postgresql", "snowflake", "mysql", "sqlite"] = Field(
        default="bigquery", description="SQL Dialect"
    )


class SchemaValidationData(BaseModel):
    is_valid: bool = Field(..., description="DDL có hợp lệ hay không")
    score: int = Field(..., ge=0, le=100, description="Điểm chất lượng thiết kế (0-100)")
    anti_pattern_warnings: list[AntiPatternWarning] = Field(
        default_factory=list, description="Danh sách cảnh báo từ Critic Agent"
    )


class ValidateSchemaResponse(BaseModel):
    status: str = Field(default="success")
    code: int = Field(default=200)
    message: str = Field(default="Validation complete")
    data: SchemaValidationData | None = Field(default=None)
    error: dict[str, Any] | None = Field(default=None)
