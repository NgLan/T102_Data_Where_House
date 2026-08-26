"""Regression tests cho stable Structured Requirement identity."""

from uuid import uuid4

import pytest
from src.application.requirements.output import GeneratedRequirement
from src.application.requirements.requirement_mapping import map_generated_requirements
from src.common.exceptions.business import BusinessException
from src.domain.requirement.entities import Requirement
from src.domain.requirement.enums import RequirementPriority, RequirementType


def test_reconciliation_preserves_unchanged_identity_and_timestamp() -> None:
    project_id = uuid4()
    current = Requirement(
        project_id=project_id,
        title="Monthly revenue",
        description="Aggregate revenue by month.",
        type=RequirementType.ANALYTICAL,
        priority=RequirementPriority.HIGH,
    )
    generated = GeneratedRequirement(
        current.title,
        current.description,
        current.type,
        current.priority,
        current.id,
    )

    reconciled = map_generated_requirements(project_id, (generated,), (current,))[0]

    assert reconciled.id == current.id
    assert reconciled.updated_at == current.updated_at


def test_reconciliation_rejects_foreign_existing_id() -> None:
    project_id = uuid4()
    generated = GeneratedRequirement(
        "Revenue",
        "Aggregate revenue.",
        RequirementType.ANALYTICAL,
        RequirementPriority.MEDIUM,
        uuid4(),
    )

    with pytest.raises(BusinessException):
        map_generated_requirements(project_id, (generated,), ())
