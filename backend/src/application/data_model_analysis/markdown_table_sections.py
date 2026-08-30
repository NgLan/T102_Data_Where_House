"""Fact, Dimension and relationship Markdown sections."""

from src.application.data_model_analysis.markdown_model_sections import is_dimension, is_fact
from src.application.data_model_analysis.models import EvidenceLevel, ModelStructure
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.requirement.entities import Requirement


def fact_analysis(
    structure: ModelStructure,
    analytical: tuple[AnalyticalRequirement, ...],
    requirements: tuple[Requirement, ...],
) -> str:
    rows = ["## Phân tích Fact Table"]
    facts = [item for item in structure.tables if is_fact(item.name)]
    for fact in facts:
        measures = [item.name for item in fact.columns if not item.is_primary_key and not item.is_foreign_key]
        foreign_keys = [item.name for item in fact.columns if item.is_foreign_key]
        grain = next((item.grain for item in analytical if item.grain), None)
        evidence = EvidenceLevel.INFERRED if grain else EvidenceLevel.UNKNOWN
        rows.append(
            f"### {fact.name}\n\n- Grain ({evidence}): {grain or 'Chưa xác định'}"
            f"\n- Measures: {', '.join(measures) or 'Chưa xác định'}"
            f"\n- Foreign keys: {', '.join(foreign_keys) or 'Không có'}"
            f"\n- Vì sao tồn tại: {_fact_reason(requirements, analytical)}"
        )
    if not facts:
        rows.append("Không phát hiện Fact theo cấu trúc/tên hiện tại.")
    return "\n\n".join(rows)


def dimension_analysis(structure: ModelStructure) -> str:
    rows = ["## Phân tích Dimension Table"]
    dimensions = [item for item in structure.tables if is_dimension(item.name)]
    for dimension in dimensions:
        keys = [item.name for item in dimension.columns if item.is_primary_key]
        attributes = [item.name for item in dimension.columns if not item.is_primary_key]
        rows.append(
            f"### {dimension.name}\n\n- Key: {', '.join(keys) or 'Chưa xác định'}"
            f"\n- Attributes: {', '.join(attributes) or 'Không có'}"
            "\n- Lý do tách Dimension (INFERRED): cung cấp ngữ cảnh mô tả để filter/group."
        )
    if not dimensions:
        rows.append("Không phát hiện Dimension theo cấu trúc/tên hiện tại.")
    return "\n\n".join(rows)


def relationship_analysis(structure: ModelStructure) -> str:
    rows = ["## Relationship Analysis"]
    rows.extend(
        f"- `{item.source}` → `{item.target}` ({item.cardinality}): khai báo trong DBML."
        for item in structure.relationships
    )
    if not structure.relationships:
        rows.append("- Không có relationship được khai báo.")
    return "\n".join(rows)


def _fact_reason(
    requirements: tuple[Requirement, ...],
    analytical: tuple[AnalyticalRequirement, ...],
) -> str:
    requirement = requirements[0].description if requirements else "chưa xác định"
    metric = next((item.metric for item in analytical if item.metric), "chưa xác định")
    return f"Requirement `{requirement}` và metric `{metric}`; liên kết này là INFERRED."
