"""Schema đầu ra có cấu trúc (Structured Output) mà LLM bắt buộc tuân theo."""

from pydantic import BaseModel, Field


class DbmlRevisionResult(BaseModel):
    """Kết quả LLM trả về khi được yêu cầu chỉnh sửa mô hình dữ liệu DBML.

    Dùng làm schema cho `ChatOpenAI.with_structured_output()` nên mọi mô tả trường ở đây
    đều được gửi kèm cho mô hình — viết bằng tiếng Anh để mô hình bám sát yêu cầu.
    """

    dbml: str = Field(
        description=(
            "The COMPLETE revised DBML document. Must contain every table of the data "
            "model, including tables that were not affected by the request. "
            "Raw DBML only - no markdown fences, no prose, no commentary."
        )
    )
    summary: str = Field(
        description=(
            "One short paragraph in Vietnamese explaining what was changed and why. "
            "This text is shown directly to the user in the chat panel."
        )
    )
    changed_tables: list[str] = Field(
        default_factory=list,
        description="Names of the tables that were added, removed or modified.",
    )


class SourceColumnItem(BaseModel):
    """Một cột trong nguồn dữ liệu do SourceDataAgent bóc tách."""

    name: str = Field(description="Column name, snake_case.")
    data_type: str = Field(
        description="Normalised data type: int, bigint, varchar, text, decimal, "
        "boolean, date, timestamp, uuid or json."
    )
    primary_key: bool = Field(default=False, description="True if this is a primary key.")
    nullable: bool = Field(default=True, description="True if the column accepts NULL.")
    unique: bool = Field(default=False, description="True if values must be unique.")
    foreign_key_reference: str | None = Field(
        default=None,
        description="Reference in the form 'other_table.column' when this is a foreign key.",
    )
    description: str | None = Field(
        default=None, description="One short sentence in Vietnamese about the column meaning."
    )


class SourceTableItem(BaseModel):
    """Một bảng trong nguồn dữ liệu do SourceDataAgent bóc tách."""

    name: str = Field(description="Table name, snake_case.")
    columns: list[SourceColumnItem] = Field(description="All columns of this table.")


class SourceRelationshipItem(BaseModel):
    """Một mối quan hệ giữa hai bảng nguồn."""

    from_column: str = Field(description="Source side in the form 'table.column'.")
    to_column: str = Field(description="Target side in the form 'table.column'.")
    type: str = Field(
        default="MANY_TO_ONE",
        description="One of ONE_TO_ONE, ONE_TO_MANY, MANY_TO_ONE, MANY_TO_MANY.",
    )


class SourceSchemaResult(BaseModel):
    """Kết quả SourceDataAgent trả về sau khi phân tích cấu trúc nguồn dữ liệu."""

    tables: list[SourceTableItem] = Field(
        description="Every table inferred from the described data sources."
    )
    relationships: list[SourceRelationshipItem] = Field(
        default_factory=list,
        description="Relationships inferred between the tables above.",
    )
    summary: str = Field(
        default="",
        description="One short paragraph in Vietnamese summarising the source structure.",
    )


class AnalyticalRequirementItem(BaseModel):
    """Một yêu cầu phân tích do RequirementAgent rút trích."""

    metric: str = Field(
        description="The measure to analyse, for example 'tổng doanh thu', 'số chuyến đi'."
    )
    dimension: str = Field(
        description="The analysis dimension, for example 'theo tài xế', 'theo khu vực'."
    )
    time_granularity: str = Field(
        description="Time grain such as 'ngày', 'tuần', 'tháng', 'quý', 'năm'."
    )
    aggregation_method: str = Field(
        description="Exactly one of SUM, AVG, COUNT, COUNT_DISTINCT, MAX, MIN."
    )
    grain: str = Field(
        description="One Vietnamese sentence describing what a single fact row represents."
    )
    source_requirement_title: str = Field(
        description="Title of the raw requirement this analytical requirement was derived from."
    )


class AnalyticalRequirementResult(BaseModel):
    """Kết quả RequirementAgent trả về sau khi phân tích yêu cầu nghiệp vụ."""

    analytical_requirements: list[AnalyticalRequirementItem] = Field(
        description="All analytical requirements extracted from the raw business requirements."
    )
    summary: str = Field(
        default="",
        description="One short paragraph in Vietnamese summarising the analysis.",
    )
