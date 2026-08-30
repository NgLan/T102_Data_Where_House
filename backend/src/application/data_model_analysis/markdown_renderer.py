"""Pure Markdown renderer for already-grounded analysis data."""

from src.application.data_model_analysis.analysis_data import AnalysisData
from src.application.data_model_analysis.markdown_localization import localize_markdown
from src.application.data_model_analysis.markdown_model_sections import (
    glossary,
    requirement_mapping,
)
from src.application.data_model_analysis.markdown_quality_sections import (
    design_rules,
    lineage,
    overview,
    uncertainties,
    validation,
)
from src.application.data_model_analysis.markdown_semantic_sections import semantic_reasoning
from src.application.data_model_analysis.markdown_table_sections import (
    dimension_analysis,
    fact_analysis,
    relationship_analysis,
)


def render_analysis_markdown(data: AnalysisData) -> str:
    context = data.context
    sections = (
        overview(data),
        glossary(context.structure),
        requirement_mapping(context.requirements, context.structure),
        fact_analysis(context.structure, context.analytical, context.requirements),
        dimension_analysis(context.structure),
        relationship_analysis(context.structure),
        semantic_reasoning(data.semantic),
        lineage(context.structure, context.sources),
        design_rules(context.structure, data.issues),
        validation(data.issues),
        uncertainties(context.structure, context.analytical, context.sources),
    )
    content = "\n\n".join(sections).strip() + "\n"
    return localize_markdown(content, context.locale)
