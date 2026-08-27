"""Domain regression tests for UNKNOWN != MISSING and coverage revisions."""

from uuid import uuid4

import pytest
from src.common.exceptions.business import BusinessException
from src.domain.analytical_requirement.enums import (
    SourceCandidateKind,
    SourceConfirmationQuestionType,
    SourceConfirmationStatus,
    SourceCoverageStatus,
)
from src.domain.analytical_requirement.source_coverage import SourceCoverageAssessment
from src.domain.analytical_requirement.source_coverage_candidate import (
    SourceCoverageCandidate,
    SourceCoverageReference,
)
from src.domain.data_source.entities import DataSource
from src.domain.data_source.enums import (
    ColumnDataType,
    DataSourceType,
    SourceSemanticDecision,
)
from src.domain.data_source.semantic_metadata import SourceSemanticAnnotation
from src.domain.data_source.value_objects import ColumnMetadata, SchemaMetadata, TableMetadata
from src.domain.project.entities import Project


def test_unknown_requires_candidate_but_missing_forbids_candidate() -> None:
    candidate = _candidate()
    with pytest.raises(BusinessException):
        SourceCoverageAssessment(
            id=uuid4(),
            batch_id=uuid4(),
            evaluated_source_revision=1,
            status=SourceCoverageStatus.NEEDS_SOURCE_CONFIRMATION,
            required_concept_key="PATIENT_IDENTITY",
            title="Identify a patient",
            explanation="Count once.",
            question="Which field?",
        )
    with pytest.raises(BusinessException):
        SourceCoverageAssessment(
            id=uuid4(),
            batch_id=uuid4(),
            evaluated_source_revision=1,
            status=SourceCoverageStatus.MISSING_SOURCE,
            required_concept_key="PATIENT_IDENTITY",
            title="Missing identity",
            explanation="No identity exists.",
            candidates=(candidate,),
        )


def test_confirmation_resolution_is_item_scoped_and_revisioned() -> None:
    candidate = _candidate()
    assessment = SourceCoverageAssessment(
        id=uuid4(),
        batch_id=uuid4(),
        evaluated_source_revision=1,
        status=SourceCoverageStatus.NEEDS_SOURCE_CONFIRMATION,
        required_concept_key="PATIENT_IDENTITY",
        title="Identify a patient",
        explanation="Count once.",
        question="Which field?",
        question_type=SourceConfirmationQuestionType.SINGLE_CANDIDATE_CONFIRMATION,
        candidates=(candidate,),
    )
    resolved = assessment.with_resolution(SourceConfirmationStatus.CONFIRMED, candidate.id)
    assert resolved.confirmation_status is SourceConfirmationStatus.CONFIRMED
    assert resolved.selected_candidate_id == candidate.id
    assert resolved.resolution_revision == 1


def test_source_confirmation_is_user_annotation_and_replacement_clears_it() -> None:
    source, unrelated = _source(), _source()
    annotation = SourceSemanticAnnotation(uuid4(), "PATIENT_IDENTITY", SourceSemanticDecision.CONFIRMED)
    assert source.annotate_column("visits", "record_no", annotation)
    assert unrelated.annotate_column("visits", "record_no", annotation)
    column = source.schema_metadata.tables[0].columns[0]  # type: ignore[union-attr]
    assert column.semantic_annotations == (annotation,)
    source.replace_file("new.csv", _schema())
    replaced = source.schema_metadata.tables[0].columns[0]  # type: ignore[union-attr]
    assert replaced.semantic_annotations == ()
    preserved = unrelated.schema_metadata.tables[0].columns[0]  # type: ignore[union-attr]
    assert preserved.semantic_annotations == (annotation,)


def test_coverage_revision_tracks_analytical_and_source_independently() -> None:
    project = Project(name="Project", user_id=uuid4(), requirement="count patients")
    project.analyzed_requirement_revision = 1
    project.derived_analytical_requirement_revision = 1
    project.mark_source_analysis_completed()
    assert not project.is_source_coverage_outdated()
    project.derived_analytical_requirement_revision = 2
    assert project.is_source_coverage_outdated()
    project.mark_source_analysis_completed()
    project.increment_source_revision()
    assert project.is_source_coverage_outdated()


def _candidate() -> SourceCoverageCandidate:
    return SourceCoverageCandidate(
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


def _schema() -> SchemaMetadata:
    column = ColumnMetadata("record_no", ColumnDataType.TEXT, distinct_count=10, is_unique_candidate=True)
    return SchemaMetadata((TableMetadata("visits", (column,), row_count=10),))


def _source() -> DataSource:
    return DataSource(
        project_id=uuid4(),
        name="visits",
        location="visits.csv",
        type=DataSourceType.CSV,
        schema_metadata=_schema(),
    )
