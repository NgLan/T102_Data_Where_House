"""Unit tests cho các thực thể và quy tắc nghiệp vụ tầng Domain (Shared & User & Project)."""

from datetime import UTC
from uuid import UUID, uuid4

import pytest
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.analytical_requirement import AggregationMethod, AnalyticalRequirement
from src.domain.data_model import (
    DataModel,
    DataModelChange,
    DataModelChangeStatus,
)
from src.domain.data_source import ColumnMetadata, DataSource, DataSourceType, SchemaMetadata, TableMetadata
from src.domain.project import Project, ProjectMember, ProjectRole, ProjectStatus
from src.domain.project_session import (
    AgentResultMetadata,
    AgentResultStatus,
    AgentType,
    MessageMetadata,
    ProjectSession,
    SessionEvent,
    SessionEventRole,
    SessionEventType,
    SessionStatus,
)
from src.domain.requirement import Requirement, RequirementPriority, RequirementType
from src.domain.shared import BaseEntity, BaseValueObject, EntityID
from src.domain.user import Email, User

# ===================================================================
# 1. BaseEntity Unit Tests
# ===================================================================

def test_base_entity_uuid_generation() -> None:
    """Tự động sinh UUIDv4 làm identity cho BaseEntity."""
    entity = BaseEntity()
    assert isinstance(entity.id, UUID)
    assert entity.id.version == 4


def test_base_entity_utc_timestamps() -> None:
    """created_at và updated_at khởi tạo dạng UTC-aware datetime."""
    entity = BaseEntity()
    assert entity.created_at.tzinfo == UTC
    assert entity.updated_at.tzinfo == UTC


def test_base_entity_mark_updated() -> None:
    """mark_updated() cập nhật mốc thời gian updated_at mới theo UTC."""
    entity = BaseEntity()
    old_updated = entity.updated_at
    entity.mark_updated()
    assert entity.updated_at >= old_updated
    assert entity.updated_at.tzinfo == UTC


def test_base_entity_equality_by_id() -> None:
    """Hai Entity cùng ID phải được xem là bằng nhau (__eq__)."""
    fixed_id = uuid4()
    e1 = BaseEntity(id=fixed_id)
    e2 = BaseEntity(id=fixed_id)
    assert e1 == e2


def test_base_entity_inequality_different_id() -> None:
    """Hai Entity khác ID không được xem là bằng nhau."""
    e1 = BaseEntity()
    e2 = BaseEntity()
    assert e1 != e2


def test_base_entity_hash_by_id() -> None:
    """Hash của Entity dựa trên ID identity."""
    fixed_id = uuid4()
    e1 = BaseEntity(id=fixed_id)
    e2 = BaseEntity(id=fixed_id)
    assert hash(e1) == hash(e2)


# ===================================================================
# 2. Email Value Object Unit Tests
# ===================================================================

def test_email_valid() -> None:
    """Khởi tạo Email hợp lệ."""
    email = Email("  user@example.com  ")
    assert email.value == "user@example.com"
    assert isinstance(email, BaseValueObject)


def test_email_empty_rejected() -> None:
    """Email rỗng bị từ chối với INVALID_EMAIL."""
    with pytest.raises(BusinessException) as exc_info:
        Email("")
    assert exc_info.value.code == ErrorCode.INVALID_EMAIL


def test_email_whitespace_only_rejected() -> None:
    """Email chỉ có khoảng trắng bị từ chối với INVALID_EMAIL."""
    with pytest.raises(BusinessException) as exc_info:
        Email("   ")
    assert exc_info.value.code == ErrorCode.INVALID_EMAIL


def test_email_missing_at_rejected() -> None:
    """Email thiếu kí tự '@' bị từ chối với INVALID_EMAIL."""
    with pytest.raises(BusinessException) as exc_info:
        Email("userexample.com")
    assert exc_info.value.code == ErrorCode.INVALID_EMAIL


def test_email_missing_domain_rejected() -> None:
    """Email thiếu domain bị từ chối với INVALID_EMAIL."""
    with pytest.raises(BusinessException) as exc_info:
        Email("user@")
    assert exc_info.value.code == ErrorCode.INVALID_EMAIL


def test_email_invalid_format_rejected() -> None:
    """Email sai format regex bị từ chối với INVALID_EMAIL."""
    with pytest.raises(BusinessException) as exc_info:
        Email("user@domain..com")
    assert exc_info.value.code == ErrorCode.INVALID_EMAIL


def test_email_immutability() -> None:
    """Email là bất biến (frozen dataclass)."""
    email = Email("user@example.com")
    with pytest.raises(AttributeError):
        email.value = "other@example.com"  # type: ignore[misc]


def test_email_equality() -> None:
    """Hai Email cùng value phải equal."""
    e1 = Email("user@example.com")
    e2 = Email("user@example.com")
    assert e1 == e2


# ===================================================================
# 3. User Entity Unit Tests
# ===================================================================

def test_user_valid_creation() -> None:
    """Khởi tạo User hợp lệ sử dụng Email Value Object."""
    user = User(username=" testuser ", email=Email("test@example.com"))
    assert user.username == "testuser"
    assert isinstance(user.email, Email)
    assert user.email.value == "test@example.com"
    assert isinstance(user.id, EntityID)


def test_user_string_email_conversion() -> None:
    """Khởi tạo User bằng chuỗi email tự động chuyển thành Email Value Object."""
    user = User(username="testuser", email="test@example.com")  # type: ignore[arg-type]
    assert isinstance(user.email, Email)
    assert user.email.value == "test@example.com"


def test_user_blank_username_rejected() -> None:
    """Username rỗng/blank bị từ chối với INVALID_USERNAME."""
    with pytest.raises(BusinessException) as exc_info:
        User(username="   ", email=Email("test@example.com"))
    assert exc_info.value.code == ErrorCode.INVALID_USERNAME


def test_user_username_too_long_rejected() -> None:
    """Username vượt quá 100 ký tự bị từ chối với USERNAME_TOO_LONG."""
    long_username = "a" * 101
    with pytest.raises(BusinessException) as exc_info:
        User(username=long_username, email=Email("test@example.com"))
    assert exc_info.value.code == ErrorCode.USERNAME_TOO_LONG


# ===================================================================
# 4. Project Entity & Domain Unit Tests
# ===================================================================

def test_project_creation_and_status_update() -> None:
    """Kiểm tra tạo Project và cập nhật trạng thái."""
    project = Project(
        name="Hệ thống Y tế",
        requirement="Phân tích doanh thu theo khoa",
        user_id=uuid4(),
    )
    assert project.status == ProjectStatus.ACTIVE
    assert project.created_at.tzinfo == UTC

    project.update_status(ProjectStatus.ANALYZING)
    assert project.status == ProjectStatus.ANALYZING


def test_project_create_owner_member() -> None:
    """Phương thức domain create_owner_member sinh ra ProjectMember với vai trò OWNER."""
    creator_id = uuid4()
    project = Project(
        name="Dự án Bệnh viện",
        requirement="Yêu cầu quản lý bệnh nhân",
        user_id=creator_id,
    )
    owner_member = project.create_owner_member()

    assert isinstance(owner_member, ProjectMember)
    assert owner_member.project_id == project.id
    assert owner_member.user_id == creator_id
    assert owner_member.role == ProjectRole.OWNER


def test_project_invalid_name() -> None:
    """Project name rỗng ném lỗi INVALID_PROJECT_NAME."""
    with pytest.raises(BusinessException) as exc_info:
        Project(name="   ", requirement="Nội dung yêu cầu")
    assert exc_info.value.code == ErrorCode.INVALID_PROJECT_NAME


def test_project_name_too_long() -> None:
    """Project name vượt quá 255 ký tự ném lỗi PROJECT_NAME_TOO_LONG."""
    with pytest.raises(BusinessException) as exc_info:
        Project(name="a" * 256, requirement="Nội dung yêu cầu")
    assert exc_info.value.code == ErrorCode.PROJECT_NAME_TOO_LONG


def test_project_invalid_requirement() -> None:
    """Project requirement rỗng ném lỗi INVALID_PROJECT_REQUIREMENT."""
    with pytest.raises(BusinessException) as exc_info:
        Project(name="Tên dự án", requirement="  ")
    assert exc_info.value.code == ErrorCode.INVALID_PROJECT_REQUIREMENT


def test_project_status_transitions() -> None:
    """Kiểm tra chuyển đổi trạng thái dự án giữa ACTIVE, ANALYZING và ARCHIVED (bao gồm unarchive)."""
    project = Project(name="Dự án cũ", requirement="Yêu cầu cũ")
    assert project.status == ProjectStatus.ACTIVE

    project.update_status(ProjectStatus.ANALYZING)
    assert project.status == ProjectStatus.ANALYZING

    project.update_status(ProjectStatus.ARCHIVED)
    assert project.status == ProjectStatus.ARCHIVED

    # Kiểm tra khôi phục lại trạng thái ACTIVE từ ARCHIVED
    project.update_status(ProjectStatus.ACTIVE)
    assert project.status == ProjectStatus.ACTIVE


# ===================================================================
# 5. Other Domain Entities Baseline Tests
# ===================================================================

def test_requirement_creation() -> None:
    """Kiểm tra tạo Requirement entity."""
    req = Requirement(
        project_id=uuid4(),
        type=RequirementType.BUSINESS,
        title="Báo cáo doanh thu",
        description="Phân tích doanh thu phòng khám",
        priority=RequirementPriority.HIGH,
    )
    assert req.type == RequirementType.BUSINESS
    assert req.priority == RequirementPriority.HIGH


def test_requirement_invalid_title() -> None:
    """Requirement title rỗng ném lỗi INVALID_REQUIREMENT_TITLE."""
    with pytest.raises(BusinessException) as exc_info:
        Requirement(title="   ", description="Mô tả")
    assert exc_info.value.code == ErrorCode.INVALID_REQUIREMENT_TITLE


def test_requirement_title_too_long() -> None:
    """Requirement title > 255 ký tự ném lỗi REQUIREMENT_TITLE_TOO_LONG."""
    with pytest.raises(BusinessException) as exc_info:
        Requirement(title="a" * 256, description="Mô tả")
    assert exc_info.value.code == ErrorCode.REQUIREMENT_TITLE_TOO_LONG


def test_requirement_invalid_description() -> None:
    """Requirement description rỗng ném lỗi INVALID_REQUIREMENT_DESCRIPTION."""
    with pytest.raises(BusinessException) as exc_info:
        Requirement(title="Tiêu đề", description="   ")
    assert exc_info.value.code == ErrorCode.INVALID_REQUIREMENT_DESCRIPTION


def test_analytical_requirement_creation() -> None:
    """Kiểm tra tạo AnalyticalRequirement entity sử dụng AggregationMethod enum."""
    ar = AnalyticalRequirement(
        requirement_id=uuid4(),
        metric="Revenue",
        dimension="Department",
        time_granularity="Month",
        aggregation_method=AggregationMethod.SUM,
    )
    assert ar.metric == "Revenue"
    assert ar.aggregation_method == AggregationMethod.SUM


def test_data_source_creation() -> None:
    """Kiểm tra tạo DataSource entity với SchemaMetadata Value Object chuẩn type safety."""
    col = ColumnMetadata(
        name="age",
        data_type="integer",
        nullable=False,
        unique=False,
        constraints=("age >= 0", "age <= 120"),
        description="Tuổi của bệnh nhân",
    )
    schema = SchemaMetadata(
        tables=(
            TableMetadata(
                name="patients",
                columns=(
                    ColumnMetadata(name="patient_id", data_type="integer", primary_key=True),
                    col,
                ),
            ),
        )
    )
    ds = DataSource(
        project_id=uuid4(),
        name="danh_sach_benh_nhan.csv",
        location="/data/files/danh_sach_benh_nhan.csv",
        type=DataSourceType.CSV,
        schema_metadata=schema,
    )
    assert ds.type == DataSourceType.CSV
    assert ds.schema_metadata is not None
    assert ds.schema_metadata.tables[0].name == "patients"
    assert ds.schema_metadata.tables[0].columns[1].constraints == ("age >= 0", "age <= 120")
    assert ds.schema_metadata.tables[0].columns[1].nullable is False


def test_agent_session_and_events() -> None:
    """Kiểm tra tạo ProjectSession và SessionEvent."""
    session = ProjectSession(
        project_id=uuid4(),
        user_id=uuid4(),
        title="Thảo luận yêu cầu",
        status=SessionStatus.ACTIVE,
    )
    assert session.status == SessionStatus.ACTIVE

    event = SessionEvent(
        session_id=session.id,
        role=SessionEventRole.AGENT,
        type=SessionEventType.MESSAGE,
        content="Tôi đã nhận yêu cầu",
        metadata=MessageMetadata(model="gemini-2.5-flash"),
    )
    assert event.role == SessionEventRole.AGENT
    assert isinstance(event.metadata, MessageMetadata)
    assert event.metadata.model == "gemini-2.5-flash"


def test_agent_result_metadata_cancelled_default_error() -> None:
    """Tự động bổ sung thông báo lỗi mặc định khi AgentResultMetadata ở trạng thái CANCELLED."""
    result = AgentResultMetadata(
        agent=AgentType.REQUIREMENT,
        status=AgentResultStatus.CANCELLED,
        session_event_id=uuid4(),
    )
    assert result.status == AgentResultStatus.CANCELLED
    assert result.error == "Agent execution was cancelled"


def test_data_model_optimistic_locking_success() -> None:
    """Kiểm tra áp dụng thay đổi DBML thành công khi revision khớp."""
    dm = DataModel(project_id=uuid4(), dbml="Table A { id uuid }", revision=1)
    change = DataModelChange(
        data_model_id=dm.id,
        user_id=uuid4(),
        base_revision=1,
        proposed_dbml="Table A { id uuid } Table B { id uuid }",
    )

    dm.apply_change(change)
    assert dm.revision == 2
    assert dm.dbml == "Table A { id uuid } Table B { id uuid }"
    assert change.status == DataModelChangeStatus.ACCEPTED


def test_data_model_optimistic_locking_conflict() -> None:
    """Kiểm tra báo lỗi xung đột khi base_revision không khớp revision hiện tại."""
    dm = DataModel(project_id=uuid4(), dbml="Table A { id uuid }", revision=2)
    change = DataModelChange(
        data_model_id=dm.id,
        user_id=uuid4(),
        base_revision=1,
        proposed_dbml="Table A { id uuid } Table B { id uuid }",
    )

    with pytest.raises(BusinessException) as exc_info:
        dm.apply_change(change)

    assert exc_info.value.code == ErrorCode.REVISION_CONFLICT
    assert change.status == DataModelChangeStatus.CONFLICTED
