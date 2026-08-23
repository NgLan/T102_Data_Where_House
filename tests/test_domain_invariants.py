"""Regression tests cho các invariant cốt lõi sau khi chuẩn hóa Domain."""

from inspect import Parameter, signature
from unittest.mock import patch
from uuid import uuid4

import pytest
from email_validator import validate_email as library_validate_email
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.data_model.entities import DataModel, DataModelChange
from src.domain.data_model.enums import DataModelChangeStatus
from src.domain.data_source.constraints import CheckConstraint
from src.domain.data_source.entities import DataSource
from src.domain.data_source.value_objects import (
    ColumnMetadata,
    ColumnUpdate,
    SchemaMetadata,
    TableMetadata,
)
from src.domain.project.entities import Project, ProjectMember
from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.project_session.enums import SessionEventRole, SessionEventType
from src.domain.requirement.entities import Requirement
from src.domain.sandbox.entities import SandboxConfig
from src.domain.sandbox.enums import SandboxDbType
from src.domain.user.value_objects import Email

VALID_DBML = "Table users { id int [pk] }"
INVALID_REFERENCE_DBML = "Table orders { user_id int [ref: > users.id] }"


@pytest.mark.parametrize(
    ("entity", "foreign_key"),
    (
        (Requirement, "project_id"),
        (Project, "user_id"),
        (ProjectMember, "project_id"),
        (ProjectMember, "user_id"),
        (AnalyticalRequirement, "requirement_id"),
        (DataSource, "project_id"),
        (DataModel, "project_id"),
        (DataModelChange, "data_model_id"),
        (DataModelChange, "user_id"),
        (ProjectSession, "project_id"),
        (ProjectSession, "user_id"),
        (SessionEvent, "session_id"),
        (SandboxConfig, "project_id"),
    ),
)
def test_foreign_keys_have_no_generated_default(entity: type, foreign_key: str) -> None:
    """Mọi khóa ngoại của entity phải được caller truyền tường minh."""
    assert signature(entity).parameters[foreign_key].default is Parameter.empty


def test_email_is_normalized_without_deliverability_lookup() -> None:
    """Email dùng validator chuẩn nhưng không kích hoạt kiểm tra DNS/network."""
    with patch(
        "src.domain.user.value_objects.validate_email",
        wraps=library_validate_email,
    ) as validator:
        email = Email(" Test@EXAMPLE.COM ")

    assert email.value == "Test@example.com"
    assert validator.call_args.kwargs["check_deliverability"] is False


def test_schema_value_objects_freeze_input_collections() -> None:
    """Collection truyền từ parser được chuyển thành tuple bất biến."""
    constraint = CheckConstraint("id > 0")
    columns = [ColumnMetadata(name="id", data_type="NUMBER", constraints=[constraint])]
    tables = [TableMetadata(name="users", columns=columns)]
    schema = SchemaMetadata(tables=tables)

    columns.append(ColumnMetadata(name="name", data_type="TEXT"))
    tables.clear()

    assert isinstance(schema.tables, tuple)
    assert isinstance(schema.tables[0].columns, tuple)
    assert schema.tables[0].columns[0].constraints == (constraint,)
    assert len(schema.tables) == 1
    assert len(schema.tables[0].columns) == 1


def test_column_update_normalizes_partial_category_values() -> None:
    """ColumnUpdate gom và chuẩn hóa toàn bộ dữ liệu của một lần chỉnh sửa cột."""
    update = ColumnUpdate(
        table_name=" users ",
        column_name=" state ",
        data_type=" category ",
        distinct_values=("active", "inactive"),
        constraints=(CheckConstraint("state <> ''"),),
    )

    assert update.table_name == "users"
    assert update.column_name == "state"
    assert update.data_type == "CATEGORY"
    assert update.distinct_values == ("active", "inactive")
    assert update.constraints == (CheckConstraint("state <> ''"),)


@pytest.mark.parametrize(
    "kwargs",
    (
        {"host": "   "},
        {"port": 0},
        {"port": 65_536},
        {"database_name": ""},
        {"schema_name": "not-valid!"},
        {"db_type": SandboxDbType.MYSQL},
    ),
)
def test_sandbox_rejects_invalid_configuration(kwargs: dict[str, object]) -> None:
    """Sandbox bảo vệ endpoint, schema và PostgreSQL-only ở Domain."""
    with pytest.raises(BusinessException) as captured:
        SandboxConfig(project_id=uuid4(), **kwargs)  # type: ignore[arg-type]

    assert captured.value.code in {
        ErrorCode.INVALID_SANDBOX_CONFIG,
        ErrorCode.UNSUPPORTED_SANDBOX_DB_TYPE,
    }


def test_session_rejects_invalid_role_event_pair() -> None:
    """Chỉ role được tài liệu hóa mới được phát từng loại session event."""
    with pytest.raises(BusinessException) as captured:
        SessionEvent(
            session_id=uuid4(),
            role=SessionEventRole.USER,
            type=SessionEventType.QUESTION,
            content="Câu hỏi",
        )

    assert captured.value.code is ErrorCode.VALIDATION_ERROR


def test_session_maps_invalid_serialized_enum_to_domain_error() -> None:
    """Enum serialize sai không được làm rò rỉ ValueError khỏi Domain."""
    with pytest.raises(BusinessException) as captured:
        SessionEvent(
            session_id=uuid4(),
            role="UNKNOWN",  # type: ignore[arg-type]
            type=SessionEventType.MESSAGE,
            content="Nội dung",
        )

    assert captured.value.code is ErrorCode.VALIDATION_ERROR


def test_data_model_only_requires_valid_dbml_syntax() -> None:
    """Domain không diễn giải reference khi DBML chỉ được lưu dưới dạng text."""
    rehydrated = DataModel(project_id=uuid4(), dbml=INVALID_REFERENCE_DBML)
    created = DataModel(project_id=uuid4(), dbml=INVALID_REFERENCE_DBML)

    assert rehydrated.dbml == INVALID_REFERENCE_DBML
    assert created.dbml == INVALID_REFERENCE_DBML


def test_accept_does_not_apply_semantic_rules_to_dbml_text() -> None:
    """DBML đúng cú pháp được áp dụng dù reference chưa có bảng đích."""
    model = DataModel(project_id=uuid4(), dbml=VALID_DBML)
    change = DataModelChange(
        data_model_id=model.id,
        user_id=uuid4(),
        base_dbml=model.dbml,
        proposed_dbml=INVALID_REFERENCE_DBML,
    )

    model.apply_change(change)

    assert model.dbml == INVALID_REFERENCE_DBML
    assert model.revision == 2
    assert change.status is DataModelChangeStatus.ACCEPTED


def test_revision_conflict_marks_proposal_without_mutating_model() -> None:
    """Conflict chỉ kết thúc proposal và giữ nguyên snapshot Data Model."""
    model = DataModel(project_id=uuid4(), dbml=VALID_DBML, revision=2)
    change = DataModelChange(
        data_model_id=model.id,
        user_id=uuid4(),
        base_revision=1,
        base_dbml=model.dbml,
        proposed_dbml="Table users { id int [pk] name varchar }",
    )

    with pytest.raises(BusinessException) as captured:
        model.apply_change(change)

    assert captured.value.code is ErrorCode.DATA_MODEL_REVISION_CONFLICT
    assert model.dbml == VALID_DBML
    assert model.revision == 2
    assert change.status is DataModelChangeStatus.CONFLICTED
