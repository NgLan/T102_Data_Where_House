"""Glossary and requirement mapping grounded in parsed DBML."""

from src.application.data_model_analysis.models import ModelStructure
from src.domain.requirement.entities import Requirement


def glossary(structure: ModelStructure) -> str:
    facts = [item.name for item in structure.tables if is_fact(item.name)]
    dimensions = [item.name for item in structure.tables if is_dimension(item.name)]
    rows = ["## Thuật ngữ"]
    if facts:
        rows.extend(
            (
                f"- **Fact Table**: bảng business event/measure. Áp dụng: {', '.join(facts)}.",
                "- **Grain**: mức chi tiết của một dòng Fact.",
            )
        )
    if dimensions:
        rows.append(f"- **Dimension Table**: ngữ cảnh filter/group. Áp dụng: {', '.join(dimensions)}.")
    if structure.relationships:
        rows.append("- **Foreign Key**: khóa liên kết được khai báo trong DBML.")
    return "\n".join(rows)


def requirement_mapping(requirements: tuple[Requirement, ...], structure: ModelStructure) -> str:
    rows = [
        "## Requirement → Model Mapping",
        "",
        "| Requirement | Thành phần model | Mức đáp ứng |",
        "|---|---|---|",
    ]
    table_tokens = [
        (table.name, tokens(table.name, *(column.name for column in table.columns))) for table in structure.tables
    ]
    for requirement in requirements:
        wanted = tokens(requirement.title, requirement.description)
        matches = [name for name, available in table_tokens if wanted & available]
        matched = set().union(*(available for _, available in table_tokens if wanted & available))
        coverage = "FULL" if wanted and wanted <= matched else "PARTIAL"
        if not matches:
            coverage = "NOT_MET"
        rows.append(f"| {requirement.title} | {', '.join(matches) or 'Chưa xác định'} | {coverage} |")
    return "\n".join(rows)


def tokens(*values: str) -> set[str]:
    return {part.casefold() for value in values for part in value.replace("_", " ").split() if len(part) > 2}


def is_fact(name: str) -> bool:
    return name.casefold().startswith("fact")


def is_dimension(name: str) -> bool:
    return name.casefold().startswith("dim")
