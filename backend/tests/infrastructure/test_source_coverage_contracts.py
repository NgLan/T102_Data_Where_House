"""Codec and deterministic grounding tests for Source Coverage."""

from uuid import uuid4

import pytest
from src.application.requirements.input import EvaluateSourceCoverageInput
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.analytical_requirement.enums import (
    SourceCandidateKind,
    SourceCoverageStatus,
)
from src.domain.analytical_requirement.source_coverage import (
    SourceCoverageAssessment,
    SourceCoverageCandidate,
)
from src.domain.data_source.entities import DataSource
from src.domain.data_source.enums import ColumnDataType, DataSourceType, SourceSemanticDecision
from src.domain.data_source.semantic_metadata import SourceSemanticAnnotation
from src.domain.data_source.value_objects import ColumnMetadata, SchemaMetadata, TableMetadata
from src.infrastructure.agents.prompts.requirement import SOURCE_COVERAGE_SYSTEM_PROMPT
from src.infrastructure.agents.source_coverage_output_mapper import map_source_coverage_result
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
        uuid4(), SourceCandidateKind.COLUMN, uuid4(), "visits", "record_no"
    )
    value = SourceCoverageAssessment(
        id=uuid4(), batch_id=uuid4(), evaluated_source_revision=3,
        status=SourceCoverageStatus.NEEDS_SOURCE_CONFIRMATION,
        required_concept_key="PATIENT_IDENTITY", title="Identify a patient",
        explanation="Two identifiers exist.", question="Which field?",
        candidates=(candidate,),
    )
    assert decode_source_coverage(encode_source_coverage((value,))) == (value,)
    assert decode_source_coverage(None) == ()
    legacy = [{
        "id": str(uuid4()), "status": "NEEDS_SOURCE_CONFIRMATION",
        "required_concept": "patient identity", "reason": "ambiguous",
        "candidates": [{
            "id": str(candidate.id), "kind": "COLUMN",
            "source_id": str(candidate.source_id), "table_name": "visits",
            "column_name": "record_no",
        }],
    }]
    restored = decode_source_coverage(legacy)[0]
    assert restored.required_concept_key == "patient identity"
    assert restored.confirmation_status.value == "PENDING"
    assert restored.evaluated_source_revision == 0


def test_mapper_rejects_invented_column_reference() -> None:
    analytical = AnalyticalRequirement(requirement_id=uuid4(), metric="patients")
    source = DataSource(
        project_id=uuid4(), name="visits", location="visits.csv",
        type=DataSourceType.CSV,
        schema_metadata=SchemaMetadata((TableMetadata(
            "visits", (ColumnMetadata("record_no", ColumnDataType.TEXT),), row_count=4,
        ),)),
    )
    payload = SourceCoverageLlmResult.model_validate({
        "outcomes": [{
            "analytical_requirement_id": analytical.id,
            "assessments": [{
                "status": "NEEDS_SOURCE_CONFIRMATION",
                    "required_concept_key": "PATIENT_IDENTITY",
                    "title": "Identify a patient",
                    "explanation": "Candidate name is not proof.",
                    "question": "Which field identifies a patient?",
                "candidates": [{
                    "kind": "COLUMN", "source_id": source.id,
                    "table_name": "visits", "column_name": "invented_patient_id",
                }],
            }],
        }],
    })
    with pytest.raises(InfrastructureException):
        map_source_coverage_result(
            payload, EvaluateSourceCoverageInput((), (analytical,), (source,))
        )


def test_schema_codec_keeps_row_count_and_user_semantics_with_legacy_defaults() -> None:
    annotation = SourceSemanticAnnotation(
        uuid4(), "PATIENT_IDENTITY", SourceSemanticDecision.CONFIRMED
    )
    schema = SchemaMetadata((TableMetadata(
        "visits",
        (ColumnMetadata("record_no", ColumnDataType.TEXT, semantic_annotations=(annotation,)),),
        row_count=12,
    ),))
    assert decode_schema_metadata(encode_schema_metadata(schema)) == schema
    legacy = {"tables": [{"name": "visits", "columns": []}], "relationships": []}
    decoded = decode_schema_metadata(legacy)
    assert decoded is not None and decoded.tables[0].row_count == 0


def test_prompt_explicitly_preserves_unknown_missing_boundary() -> None:
    assert "UNKNOWN is not MISSING" in SOURCE_COVERAGE_SYSTEM_PROMPT
    assert "profile statistics may" in SOURCE_COVERAGE_SYSTEM_PROMPT
    assert "do not prove business meaning" in SOURCE_COVERAGE_SYSTEM_PROMPT
    assert "Never invent a desired column name" in SOURCE_COVERAGE_SYSTEM_PROMPT
