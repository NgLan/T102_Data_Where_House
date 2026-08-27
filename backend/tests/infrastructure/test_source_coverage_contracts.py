"""Codec and deterministic grounding tests for Source Coverage."""

from uuid import uuid4

import pytest
from src.application.requirements.input import EvaluateSourceCoverageInput, RequirementContext
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.analytical_requirement.enums import (
    SourceCandidateKind,
    SourceConfirmationQuestionType,
    SourceCoverageStatus,
)
from src.domain.analytical_requirement.source_coverage import SourceCoverageAssessment
from src.domain.analytical_requirement.source_coverage_candidate import (
    SourceCoverageCandidate,
    SourceCoverageReference,
)
from src.domain.data_source.entities import DataSource
from src.domain.data_source.enums import ColumnDataType, DataSourceType, SourceSemanticDecision
from src.domain.data_source.semantic_metadata import SourceSemanticAnnotation
from src.domain.data_source.value_objects import ColumnMetadata, SchemaMetadata, TableMetadata
from src.infrastructure.agents.prompts.requirement import SOURCE_COVERAGE_SYSTEM_PROMPT
from src.infrastructure.agents.source_coverage_context_renderer import (
    render_source_coverage_input,
)
from src.infrastructure.agents.source_coverage_output_mapper import map_source_coverage_result
from src.infrastructure.agents.transport_references import (
    SourceCoverageReferenceBoundary,
    TransportReferenceMap,
)
from src.infrastructure.database.mappers.data_source.schema_metadata_codec import (
    decode_schema_metadata,
    encode_schema_metadata,
)
from src.infrastructure.database.mappers.source_coverage_codec import (
    decode_source_coverage,
    encode_source_coverage,
)
from src.infrastructure.llm.source_coverage_structured_outputs import SourceCoverageLlmResult


def test_coverage_codec_round_trip_and_legacy_default() -> None:
    candidate = SourceCoverageCandidate(
        uuid4(),
        "Record number",
        (
            SourceCoverageReference(
                SourceCandidateKind.COLUMN,
                uuid4(),
                table_name="visits",
                column_name="record_no",
            ),
        ),
    )
    value = SourceCoverageAssessment(
        id=uuid4(),
        batch_id=uuid4(),
        evaluated_source_revision=3,
        status=SourceCoverageStatus.NEEDS_SOURCE_CONFIRMATION,
        required_concept_key="PATIENT_IDENTITY",
        title="Identify a patient",
        explanation="Two identifiers exist.",
        question="Which field?",
        question_type=SourceConfirmationQuestionType.SINGLE_CANDIDATE_CONFIRMATION,
        candidates=(candidate,),
    )
    assert decode_source_coverage(encode_source_coverage((value,))) == (value,)
    assert decode_source_coverage(None) == ()
    legacy = [
        {
            "id": str(uuid4()),
            "status": "NEEDS_SOURCE_CONFIRMATION",
            "required_concept": "patient identity",
            "reason": "ambiguous",
            "candidates": [
                {
                    "id": str(candidate.id),
                    "kind": "COLUMN",
                    "source_id": str(candidate.references[0].source_id),
                    "table_name": "visits",
                    "column_name": "record_no",
                }
            ],
        }
    ]
    restored = decode_source_coverage(legacy)[0]
    assert restored.required_concept_key == "patient identity"
    assert restored.confirmation_status.value == "PENDING"
    assert restored.evaluated_source_revision == 0


def test_mapper_rejects_invented_column_reference() -> None:
    analytical = AnalyticalRequirement(requirement_id=uuid4(), metric="patients")
    source = DataSource(
        project_id=uuid4(),
        name="visits",
        location="visits.csv",
        type=DataSourceType.CSV,
        schema_metadata=SchemaMetadata(
            (
                TableMetadata(
                    "visits",
                    (ColumnMetadata("record_no", ColumnDataType.TEXT),),
                    row_count=4,
                ),
            )
        ),
    )
    payload = SourceCoverageLlmResult.model_validate(
        {
            "outcomes": [
                {
                    "analytical_requirement_ref": "A1",
                    "assessments": [
                        {
                            "status": "NEEDS_SOURCE_CONFIRMATION",
                            "required_concept_key": "PATIENT_IDENTITY",
                            "title": "Identify a patient",
                            "explanation": "Candidate name is not proof.",
                            "question": "Which field identifies a patient?",
                            "question_type": "SINGLE_CANDIDATE_CONFIRMATION",
                            "candidates": [
                                {
                                    "label": "Patient number",
                                    "references": [
                                        {
                                            "kind": "COLUMN",
                                            "source_ref": "S1",
                                            "table_name": "visits",
                                            "column_name": "invented_patient_id",
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
        }
    )
    with pytest.raises(InfrastructureException):
        map_source_coverage_result(payload, EvaluateSourceCoverageInput((), (analytical,), (source,)))


def test_schema_codec_keeps_row_count_and_user_semantics_with_legacy_defaults() -> None:
    annotation = SourceSemanticAnnotation(
        uuid4(),
        "TREATMENT_DURATION",
        SourceSemanticDecision.CONFIRMED,
        candidate_label="Admission to discharge",
        role_key="START_TIME",
        role_label="Treatment start",
    )
    schema = SchemaMetadata(
        (
            TableMetadata(
                "visits",
                (ColumnMetadata("record_no", ColumnDataType.TEXT, semantic_annotations=(annotation,)),),
                row_count=12,
            ),
        )
    )
    assert decode_schema_metadata(encode_schema_metadata(schema)) == schema
    legacy = {"tables": [{"name": "visits", "columns": []}], "relationships": []}
    decoded = decode_schema_metadata(legacy)
    assert decoded is not None and decoded.tables[0].row_count == 0


def test_prompt_explicitly_preserves_unknown_missing_boundary() -> None:
    assert "UNKNOWN is not MISSING" in SOURCE_COVERAGE_SYSTEM_PROMPT
    assert "profile statistics may" in SOURCE_COVERAGE_SYSTEM_PROMPT
    assert "do not prove business meaning" in SOURCE_COVERAGE_SYSTEM_PROMPT
    assert "Never invent a desired column name" in SOURCE_COVERAGE_SYSTEM_PROMPT
    for question_type in SourceConfirmationQuestionType:
        assert question_type.value in SOURCE_COVERAGE_SYSTEM_PROMPT
    assert "matching admission and discharge" in SOURCE_COVERAGE_SYSTEM_PROMPT
    assert "department should receive the treatment episode" in SOURCE_COVERAGE_SYSTEM_PROMPT


def test_source_coverage_renderer_uses_refs_and_drops_stale_annotations() -> None:
    requirement_id, stale_id, project_id = uuid4(), uuid4(), uuid4()
    annotations = (
        SourceSemanticAnnotation(
            requirement_id,
            "CURRENT_CONCEPT",
            SourceSemanticDecision.CONFIRMED,
        ),
        SourceSemanticAnnotation(
            stale_id,
            "STALE_CONCEPT",
            SourceSemanticDecision.CONFIRMED,
        ),
    )
    requirement = RequirementContext(requirement_id, "Revenue", "Monthly revenue", "ANALYTICAL", "HIGH")
    analytical = AnalyticalRequirement(requirement_id=requirement_id, metric="revenue")
    source = DataSource(
        project_id=project_id,
        name="sales",
        location="sales.csv",
        schema_metadata=SchemaMetadata(
            tables=(
                TableMetadata(
                    "sales",
                    (ColumnMetadata("amount", "DECIMAL", semantic_annotations=annotations),),
                ),
            )
        ),
    )
    references = SourceCoverageReferenceBoundary(
        TransportReferenceMap.create("R", (requirement_id,)),
        TransportReferenceMap.create("A", (analytical.id,)),
        TransportReferenceMap.create("S", (source.id,)),
    )

    rendered = render_source_coverage_input(
        EvaluateSourceCoverageInput((requirement,), (analytical,), (source,)), references
    )
    combined = "".join(rendered)

    assert all(str(value) not in combined for value in (requirement_id, stale_id, analytical.id, source.id))
    assert "CURRENT_CONCEPT" in combined
    assert "STALE_CONCEPT" not in combined
    assert '"requirement_ref": "R1"' in combined
