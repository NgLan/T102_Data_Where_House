"""Markdown rendering for grounded semantic observations."""

from src.application.data_model_analysis.models import AnalysisSemanticOutput


def semantic_reasoning(output: AnalysisSemanticOutput) -> str:
    rows = ["## Semantic Reasoning / Mapping"]
    for item in output.observations:
        references = ".".join(value for value in (item.table_name, item.column_name) if value)
        canonical = ", ".join(
            value
            for value in (
                references,
                str(item.requirement_id) if item.requirement_id else "",
                str(item.source_id) if item.source_id else "",
            )
            if value
        )
        rows.append(f"- **{item.evidence}** {item.explanation} — evidence: {canonical or 'UNKNOWN'}")
    if not output.observations:
        rows.append("- Không có kết luận semantic bổ sung.")
    rows.extend(f"- Uncertainty: {item}" for item in output.uncertainties)
    return "\n".join(rows)
