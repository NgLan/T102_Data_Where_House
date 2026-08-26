"""Structured-output contracts ngăn Agent lấp đầy dữ liệu không có căn cứ."""

from uuid import uuid4

import pytest
from pydantic import ValidationError
from src.application.data_warehouse_workflows.generated_entity_mapper import (
    map_generated_analytical,
)
from src.application.project_sessions.conversation_context import (
    ConversationInputKind,
    ConversationMemory,
    PendingClarificationContext,
)
from src.application.requirements.input import ClarifyRequirementsInput
from src.application.requirements.output import GeneratedAnalyticalRequirement
from src.common.exceptions.business import BusinessException
from src.domain.analytical_requirement.enums import AggregationMethod
from src.domain.project_session.conversation_summary import (
    ConversationSummary,
    SummaryDecision,
)
from src.infrastructure.agents.requirement_context_renderer import (
    render_requirement_clarification,
)
from src.infrastructure.llm.agent_structured_outputs import (
    AnalyticalDerivationOutcome,
    AnalyticalRequirementItem,
    AnalyticalRequirementResult,
    DwConversationResult,
    GeneratedRequirementItem,
    RequirementClarificationResult,
)
from src.infrastructure.llm.conversation_summary_output import SummaryDecisionOutput


def _ambiguous_requirement() -> GeneratedRequirementItem:
    return GeneratedRequirementItem(
        title="Phân tích số lượng bệnh nhân theo năm",
        description="Phân tích số lượng bệnh nhân theo năm.",
        requirement_type="ANALYTICAL",
        priority="MEDIUM",
        existing_requirement_id=None,
    )


def test_ambiguous_count_can_return_one_grounded_question() -> None:
    result = RequirementClarificationResult(
        requirements=[_ambiguous_requirement()],
        status="NEEDS_CLARIFICATION",
        question='Bạn muốn "số lượng bệnh nhân" được tính như thế nào?',
        options=["Mỗi bệnh nhân một lần trong năm"],
        allow_custom_answer=True,
        reason="Chưa xác định đơn vị đếm của chỉ số.",
        summary="Cần làm rõ cách đếm bệnh nhân.",
    )
    serialized = result.model_dump_json()
    assert result.status == "NEEDS_CLARIFICATION"
    assert "bác sĩ" not in serialized
    assert "khoa" not in serialized


def test_requirement_clarification_requires_concrete_reason() -> None:
    with pytest.raises(ValidationError):
        RequirementClarificationResult(
            requirements=[_ambiguous_requirement()],
            status="NEEDS_CLARIFICATION",
            question="Bạn muốn đếm theo cách nào?",
            options=["Một lần trong năm"],
            allow_custom_answer=True,
            summary="Cần làm rõ cách đếm.",
        )


def test_missing_optional_dimensions_do_not_prevent_ready_contract() -> None:
    result = RequirementClarificationResult(
        requirements=[
            GeneratedRequirementItem(
                title="Đếm bệnh nhân duy nhất theo năm",
                description="Mỗi bệnh nhân được tính một lần trong từng năm.",
                requirement_type="ANALYTICAL",
                priority="MEDIUM",
                existing_requirement_id=None,
            )
        ],
        status="READY",
        allow_custom_answer=True,
        summary="Yêu cầu đã đủ rõ để tiếp tục.",
    )
    assert result.status == "READY"
    assert result.question is None
    assert result.allow_custom_answer is False


def test_ready_result_automatically_clears_clarification_fields() -> None:
    result = RequirementClarificationResult(
        requirements=[_ambiguous_requirement()],
        status="READY",
        question="Bạn muốn đếm theo cách nào?",
        options=["Một lần", "Nhiều lần"],
        allow_custom_answer=True,
        reason="Lý do không cần thiết khi đã ready.",
        summary="Đã sẵn sàng.",
    )
    assert result.status == "READY"
    assert result.question is None
    assert result.options == []
    assert result.allow_custom_answer is False
    assert result.reason is None


def test_analytical_fields_accept_null_but_reject_empty_text() -> None:
    item = AnalyticalRequirementItem(source_requirement_id=str(uuid4()))
    assert item.aggregation_method is None
    with pytest.raises(ValidationError):
        AnalyticalRequirementItem(source_requirement_id=str(uuid4()), grain="")


def test_clear_requirement_with_missing_source_is_traced_as_source_gap() -> None:
    requirement_id = str(uuid4())
    clarification = RequirementClarificationResult(
        requirements=[
            GeneratedRequirementItem(
                title="Phân tích theo bác sĩ",
                description="Đếm lượt khám theo từng bác sĩ mỗi tháng.",
                requirement_type="ANALYTICAL",
                priority="MEDIUM",
                existing_requirement_id=None,
            )
        ],
        status="READY",
        summary="Ngữ nghĩa nghiệp vụ đã rõ.",
    )
    result = AnalyticalRequirementResult(
        outcomes=[
            AnalyticalDerivationOutcome(
                source_requirement_id=requirement_id,
                status="SOURCE_GAP",
                source_gap={
                    "gap_kind": "MISSING_DATA",
                    "missing_concepts": ["doctor identifier"],
                    "reason": "SchemaMetadata has no doctor identifier or relationship.",
                    "suggested_source_fields": ["doctor identity data"],
                    "suggested_action": "ADD_OR_REPLACE_SOURCE",
                },
            )
        ]
    )
    assert clarification.status == "READY"
    assert result.outcomes[0].status == "SOURCE_GAP"
    assert result.outcomes[0].analytical_requirements == []


def test_patient_id_does_not_hide_count_semantic_gap() -> None:
    outcome = AnalyticalDerivationOutcome(
        source_requirement_id=str(uuid4()),
        status="NEEDS_REQUIREMENT_CLARIFICATION",
        reason="Patient count does not define event count versus distinct patients.",
    )
    assert outcome.status == "NEEDS_REQUIREMENT_CLARIFICATION"


def test_technical_requirement_has_explicit_non_analytical_outcome() -> None:
    outcome = AnalyticalDerivationOutcome(
        source_requirement_id=str(uuid4()),
        status="NOT_ANALYTICAL",
        reason="This deployment constraint requests no analysis.",
    )
    assert outcome.status == "NOT_ANALYTICAL"


def test_ready_derivation_requires_grounded_item_with_matching_id() -> None:
    requirement_id = str(uuid4())
    with pytest.raises(ValidationError):
        AnalyticalDerivationOutcome(
            source_requirement_id=requirement_id,
            status="READY",
        )
    with pytest.raises(ValidationError):
        AnalyticalDerivationOutcome(
            source_requirement_id=requirement_id,
            status="READY",
            analytical_requirements=[AnalyticalRequirementItem(source_requirement_id=str(uuid4()))],
        )


def test_analytical_mapper_preserves_null_fields() -> None:
    requirement_id = uuid4()
    generated = GeneratedAnalyticalRequirement(requirement_id, None, None, None, None, None)
    entity = map_generated_analytical((generated,), {requirement_id})[0]
    assert entity.metric is None
    assert entity.aggregation_method is None


def test_distinct_patient_and_visit_count_remain_different() -> None:
    requirement_id = uuid4()
    generated = (
        GeneratedAnalyticalRequirement(
            requirement_id,
            "unique patients within each year",
            "year",
            "YEAR",
            "COUNT_DISTINCT",
            "one patient per year",
        ),
        GeneratedAnalyticalRequirement(
            requirement_id,
            "patient visits",
            "year",
            "YEAR",
            "COUNT",
            "one visit",
        ),
    )
    distinct, visits = map_generated_analytical(generated, {requirement_id})
    assert distinct.aggregation_method is AggregationMethod.COUNT_DISTINCT
    assert visits.aggregation_method is AggregationMethod.COUNT


def test_agent_outputs_forbid_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        AnalyticalRequirementItem(source_requirement_id=str(uuid4()), invented_source_column="patient_id")


def test_dw_clarification_requires_reason() -> None:
    with pytest.raises(ValidationError):
        DwConversationResult(
            kind="clarification",
            question="Chọn grain nào?",
            options=["Một giao dịch"],
            allow_custom_answer=True,
            reason=None,
            dbml=None,
            summary="Cần làm rõ grain.",
        )


def test_renderer_distinguishes_pending_answer_from_normal_message() -> None:
    pending = PendingClarificationContext(uuid4(), uuid4(), "Đếm như thế nào?", ("Một lần",), None, "counting unit")
    memory = ConversationMemory(
        None,
        (),
        "Mỗi bệnh nhân chỉ tính một lần trong từng năm.",
        ConversationInputKind.CLARIFICATION_ANSWER,
        pending,
    )
    sections = render_requirement_clarification(ClarifyRequirementsInput("Số lượng bệnh nhân theo năm", (), (), memory))
    assert sections["input_kind"] == "CLARIFICATION_ANSWER"
    assert sections["current_input"] == memory.current_input
    assert "counting unit" in sections["pending_clarification"]


def test_summary_decision_requires_evidence() -> None:
    with pytest.raises(ValidationError):
        SummaryDecisionOutput(key="patient_count", value="distinct patients")


def test_summary_rejects_two_active_values_for_same_semantic_key() -> None:
    event_id = uuid4()
    with pytest.raises(BusinessException):
        ConversationSummary(
            confirmed_decisions=(
                SummaryDecision("patient_count", "visit count", (event_id,)),
                SummaryDecision("PATIENT_COUNT", "distinct patients", (event_id,)),
            )
        )
