"""Markdown sections grounded in project context and deterministic validation."""

from src.application.data_model_analysis.analysis_data import AnalysisData
from src.application.data_model_analysis.markdown_model_sections import is_dimension, is_fact
from src.application.data_model_analysis.models import EvidenceLevel, ModelStructure
from src.application.data_warehouse_workflows.output import ValidationIssue
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.data_source.entities import DataSource


def overview(data: AnalysisData) -> str:
    context = data.context
    project = context.project
    requirements = context.requirements
    analytical = context.analytical
    requirement_rows = "\n".join(f"- {item.title}: {item.description}" for item in requirements) or "- Chưa có"
    metric_rows = (
        "\n".join(f"- {item.metric or 'Chưa xác định'} / {item.grain or 'grain chưa rõ'}" for item in analytical)
        or "- Chưa có"
    )
    objective = project.description or project.requirement or "Chưa xác định"
    proposal = f"\n- Proposal ID: {data.proposal_change_id}" if data.proposal_change_id else ""
    return (
        "# Phân tích Data Warehouse\n\n## Tổng quan"
        f"\n\n- Project: {project.name}\n- Target: {data.target_kind.value}"
        f"\n- Current revision: {data.current_revision or data.revision}"
        f"\n- Base revision: {data.base_revision or data.revision}{proposal}"
        f"\n- Mục tiêu: {objective}\n\n### Requirements chính\n{requirement_rows}"
        f"\n\n### Analytical Requirements chính\n{metric_rows}"
    )


def lineage(structure: ModelStructure, sources: tuple[DataSource, ...]) -> str:
    source_tables = {
        table.name.casefold(): f"{source.name}.{table.name}"
        for source in sources
        if source.schema_metadata
        for table in source.schema_metadata.tables
    }
    rows = ["## Source → Target / Lineage"]
    for table in structure.tables:
        source = source_tables.get(table.name.casefold())
        level = EvidenceLevel.CONFIRMED if source else EvidenceLevel.UNKNOWN
        rows.append(f"- {source or 'Chưa xác định'} → {table.name} — **{level}**")
    return "\n".join(rows)


def design_rules(structure: ModelStructure, issues: tuple[ValidationIssue, ...]) -> str:
    fact_count = sum(is_fact(item.name) for item in structure.tables)
    dimension_count = sum(is_dimension(item.name) for item in structure.tables)
    return (
        "## Đánh giá theo Data Warehouse Design Rules"
        f"\n\n- Fact tables: {fact_count}; Dimension tables: {dimension_count}."
        f"\n- Relationships: {len(structure.relationships)}."
        f"\n- Validation Engine là source of truth và trả {len(issues)} issue(s)."
        "\n- Kết luận thiếu evidence được giữ là uncertainty, không tạo rule violation mới."
    )


def validation(issues: tuple[ValidationIssue, ...]) -> str:
    rows = ["## Cảnh báo và gợi ý cải thiện"]
    for issue in issues:
        target = ".".join(item for item in (issue.table_name, issue.column_name) if item) or "Toàn mô hình"
        rows.append(
            f"### {issue.severity} — {target}\n\n- Vấn đề: {issue.title}"
            f"\n- Lý do: {issue.description}"
            f"\n- Ảnh hưởng: mô hình có thể vi phạm rule `{issue.code}`."
            "\n- Gợi ý: chỉnh đúng object nêu trên rồi chạy lại Validation Engine."
        )
    if not issues:
        rows.append("Không có issue deterministic tại revision này.")
    return "\n\n".join(rows)


def uncertainties(
    structure: ModelStructure,
    analytical: tuple[AnalyticalRequirement, ...],
    sources: tuple[DataSource, ...],
) -> str:
    rows = ["## Các điểm chưa xác định / cần xác nhận"]
    if any(not item.grain for item in analytical):
        rows.append("- Một hoặc nhiều Analytical Requirement chưa xác định grain.")
    if not sources:
        rows.append("- Chưa có Source Metadata để chứng minh lineage.")
    missing_keys = any(
        is_dimension(table.name) and not any(column.is_primary_key for column in table.columns)
        for table in structure.tables
    )
    if missing_keys:
        rows.append("- Có Dimension chưa xác định được key đáng tin cậy.")
    rows.append("- SCD strategy cần Requirement hoặc metadata có evidence rõ ràng.")
    return "\n".join(rows)
