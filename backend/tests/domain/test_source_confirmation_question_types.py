"""Structural contracts cho năm loại Source Confirmation."""

from uuid import uuid4

import pytest
from src.common.exceptions.business import BusinessException
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


def test_all_question_types_accept_only_their_complete_answer_shape() -> None:
    single_a, single_b = (
        _mapping("Patient record", _column("record_no")),
        _mapping("Medical record", _column("medical_no")),
    )
    field_set = _mapping(
        "Treatment duration",
        _column("admitted_at", "START_TIME", "Treatment start"),
        _column("discharged_at", "END_TIME", "Treatment end"),
    )
    relationship = _mapping("Patient to archive", _relationship())
    cases = (
        (SourceConfirmationQuestionType.SINGLE_FIELD_SELECTION, (single_a, single_b)),
        (SourceConfirmationQuestionType.FIELD_SET_CONFIRMATION, (field_set,)),
        (SourceConfirmationQuestionType.BUSINESS_SEMANTIC_CHOICE, (single_a, single_b)),
        (SourceConfirmationQuestionType.SINGLE_CANDIDATE_CONFIRMATION, (single_a,)),
        (SourceConfirmationQuestionType.RELATIONSHIP_CONFIRMATION, (relationship,)),
    )
    for question_type, candidates in cases:
        assert _assessment(question_type, candidates).question_type is question_type


def test_question_type_rejects_incomplete_answer_shape() -> None:
    cases = (
        (SourceConfirmationQuestionType.SINGLE_FIELD_SELECTION, (_mapping("One", _column("a")),)),
        (SourceConfirmationQuestionType.FIELD_SET_CONFIRMATION, (_mapping("One", _column("a")),)),
        (SourceConfirmationQuestionType.SINGLE_CANDIDATE_CONFIRMATION, (_mapping("Two", _column("a"), _column("b")),)),
        (SourceConfirmationQuestionType.RELATIONSHIP_CONFIRMATION, (_mapping("Column", _column("a")),)),
    )
    for question_type, candidates in cases:
        with pytest.raises(BusinessException):
            _assessment(question_type, candidates)


def test_non_confirmation_status_forbids_question_contract() -> None:
    candidate = _mapping("Patient record", _column("record_no"))
    with pytest.raises(BusinessException):
        SourceCoverageAssessment(
            id=uuid4(),
            batch_id=uuid4(),
            evaluated_source_revision=1,
            status=SourceCoverageStatus.SUPPORTED,
            required_concept_key="PATIENT_IDENTITY",
            title="Patient identity",
            explanation="Directly supported.",
            candidates=(candidate,),
        )
    with pytest.raises(BusinessException):
        SourceCoverageAssessment(
            id=uuid4(),
            batch_id=uuid4(),
            evaluated_source_revision=1,
            status=SourceCoverageStatus.SUPPORTED,
            required_concept_key="PATIENT_IDENTITY",
            title="Patient identity",
            explanation="Directly supported.",
            question_type=SourceConfirmationQuestionType.SINGLE_CANDIDATE_CONFIRMATION,
        )


def test_mapping_rejects_same_physical_reference_with_different_roles() -> None:
    source_id = uuid4()
    references = tuple(
        SourceCoverageReference(
            SourceCandidateKind.COLUMN,
            source_id,
            role_key,
            role_label,
            table_name="visits",
            column_name="event_at",
        )
        for role_key, role_label in (
            ("START_TIME", "Treatment start"),
            ("END_TIME", "Treatment end"),
        )
    )

    with pytest.raises(BusinessException):
        _mapping("Treatment duration", *references)


def _assessment(
    question_type: SourceConfirmationQuestionType,
    candidates: tuple[SourceCoverageCandidate, ...],
) -> SourceCoverageAssessment:
    return SourceCoverageAssessment(
        id=uuid4(),
        batch_id=uuid4(),
        evaluated_source_revision=1,
        status=SourceCoverageStatus.NEEDS_SOURCE_CONFIRMATION,
        required_concept_key="CONCEPT",
        title="Confirm source",
        explanation="The answer changes the result.",
        question="Which answer applies?",
        question_type=question_type,
        candidates=candidates,
    )


def _mapping(label: str, *references: SourceCoverageReference) -> SourceCoverageCandidate:
    return SourceCoverageCandidate(uuid4(), label, references)


def _column(
    name: str,
    role_key: str | None = None,
    role_label: str | None = None,
) -> SourceCoverageReference:
    return SourceCoverageReference(
        SourceCandidateKind.COLUMN,
        uuid4(),
        role_key,
        role_label,
        table_name="visits",
        column_name=name,
    )


def _relationship() -> SourceCoverageReference:
    return SourceCoverageReference(
        SourceCandidateKind.RELATIONSHIP,
        uuid4(),
        from_column="patients.record_no",
        to_column="archive.record_no",
    )
