"""Unit tests chi tiết cho toàn bộ các Domain ↔ Persistence Mappers."""

from datetime import UTC, datetime
from uuid import uuid4

from src.domain.data_model.entities import DataModel, DataModelChange
from src.domain.data_model.enums import DataModelChangeStatus
from src.domain.data_source.entities import DataSource
from src.domain.data_source.enums import DataSourceType, RelationshipType
from src.domain.data_source.value_objects import (
    ColumnMetadata,
    RelationshipMetadata,
    SchemaMetadata,
    TableMetadata,
)
from src.domain.project.entities import Project
from src.domain.project.enums import ProjectStatus
from src.domain.project_session.entities import SessionEvent
from src.domain.project_session.enums import (
    AgentResultStatus,
    AgentType,
    SessionEventRole,
    SessionEventType,
)
from src.domain.project_session.value_objects import (
    AgentResultMetadata,
    LLMCallStats,
)
from src.domain.requirement.entities import Requirement
from src.domain.requirement.enums import RequirementPriority, RequirementType
from src.domain.user.entities import User
from src.domain.user.value_objects import Email
from src.infrastructure.database.mappers import (
    DataModelChangeMapper,
    DataModelMapper,
    DataSourceMapper,
    ProjectMapper,
    RequirementMapper,
    SessionEventMapper,
    UserMapper,
)

SIMPLE_DBML = "Table users { id int [pk] }"


def test_user_mapper_domain_to_model_and_back() -> None:
    """Test UserMapper hai chiều và đảm bảo giữ nguyên timestamps."""
    created_ts = datetime(2026, 8, 13, 10, 0, 0, tzinfo=UTC)
    updated_ts = datetime(2026, 8, 13, 11, 0, 0, tzinfo=UTC)
    user_id = uuid4()

    entity = User(
        id=user_id,
        username="john_doe",
        email=Email(value="john@example.com"),
        created_at=created_ts,
        updated_at=updated_ts,
    )

    model = UserMapper.to_model(entity)
    assert model.id == user_id
    assert model.username == "john_doe"
    assert model.created_at == created_ts
    assert model.updated_at == updated_ts

    restored_entity = UserMapper.to_domain(model)
    assert restored_entity.id == entity.id
    assert restored_entity.username == entity.username
    assert restored_entity.email == entity.email
    assert restored_entity.created_at == created_ts
    assert restored_entity.updated_at == updated_ts


def test_project_mapper_domain_to_model_and_back() -> None:
    """Test ProjectMapper hai chiều."""
    proj_id = uuid4()
    user_id = uuid4()
    created_ts = datetime(2026, 8, 13, 10, 0, 0, tzinfo=UTC)
    updated_ts = datetime(2026, 8, 13, 11, 0, 0, tzinfo=UTC)

    entity = Project(
        id=proj_id,
        name="Test Project",
        requirement="Sales Analytics System",
        user_id=user_id,
        description="Detailed description",
        domain="Retail",
        status=ProjectStatus.ANALYZING,
        created_at=created_ts,
        updated_at=updated_ts,
    )

    model = ProjectMapper.to_model(entity)
    assert model.id == proj_id
    assert model.name == "Test Project"
    assert model.status == "ANALYZING"

    restored = ProjectMapper.to_domain(model)
    assert restored.id == proj_id
    assert restored.status == ProjectStatus.ANALYZING
    assert restored.created_at == created_ts
    assert restored.updated_at == updated_ts


def test_data_source_mapper_schema_metadata() -> None:
    """Test DataSourceMapper serialization/deserialization cho SchemaMetadata."""
    ds_id = uuid4()
    proj_id = uuid4()

    schema = SchemaMetadata(
        tables=(
            TableMetadata(
                name="orders",
                columns=(
                    ColumnMetadata(
                        name="id",
                        data_type="INTEGER",
                        primary_key=True,
                        nullable=False,
                    ),
                    ColumnMetadata(
                        name="total",
                        data_type="DECIMAL",
                        nullable=False,
                    ),
                ),
            ),
        ),
        relationships=(
            RelationshipMetadata(
                from_column="orders.customer_id",
                to_column="customers.id",
                type=RelationshipType.MANY_TO_ONE,
            ),
        ),
    )

    entity = DataSource(
        id=ds_id,
        project_id=proj_id,
        name="Postgres DB",
        location="localhost:5432",
        type=DataSourceType.SQL,
        schema_metadata=schema,
    )

    model = DataSourceMapper.to_model(entity)
    assert model.schema_metadata is not None
    assert "tables" in model.schema_metadata
    assert model.schema_metadata["tables"][0]["name"] == "orders"

    restored = DataSourceMapper.to_domain(model)
    assert restored.schema_metadata is not None
    assert len(restored.schema_metadata.tables) == 1
    assert restored.schema_metadata.tables[0].name == "orders"
    assert restored.schema_metadata.relationships[0].type == RelationshipType.MANY_TO_ONE


def test_session_event_mapper_metadata_types() -> None:
    """Test SessionEventMapper serialization/deserialization cho các loại SessionEventMetadata."""
    session_id = uuid4()
    event_id = uuid4()

    # AgentResultMetadata
    agent_result_meta = AgentResultMetadata(
        agent=AgentType.REQUIREMENT,
        status=AgentResultStatus.SUCCESS,
        session_event_id=event_id,
        output_data="Requirement analyzed",
        llm=LLMCallStats(
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
        ),
    )

    entity = SessionEvent(
        id=event_id,
        session_id=session_id,
        role=SessionEventRole.AGENT,
        type=SessionEventType.AGENT_RESULT,
        content="Success",
        metadata=agent_result_meta,
    )

    model = SessionEventMapper.to_model(entity)
    assert model.event_metadata is not None
    assert model.event_metadata["agent"] == "RequirementAgent"
    assert model.event_metadata["status"] == "SUCCESS"

    restored = SessionEventMapper.to_domain(model)
    assert isinstance(restored.metadata, AgentResultMetadata)
    assert restored.metadata.agent == AgentType.REQUIREMENT
    assert restored.metadata.status == AgentResultStatus.SUCCESS
    assert restored.metadata.llm is not None
    assert restored.metadata.llm.model == "gpt-4o"


def test_requirement_mapper_preserves_serialized_enum_values() -> None:
    """Requirement mapper đọc và ghi đúng các enum value đang lưu trong database."""
    entity = Requirement(
        project_id=uuid4(),
        type=RequirementType.BUSINESS,
        title="Doanh thu",
        description="Theo dõi doanh thu theo tháng",
        priority=RequirementPriority.HIGH,
    )

    model = RequirementMapper.to_model(entity)
    restored = RequirementMapper.to_domain(model)

    assert model.type == "BUSINESS"
    assert model.priority == "HIGH"
    assert restored.type is RequirementType.BUSINESS
    assert restored.priority is RequirementPriority.HIGH


def test_data_model_change_mapper_preserves_status_and_foreign_keys() -> None:
    """Proposal mapper round-trip giữ nguyên wire value và identity liên kết."""
    entity = DataModelChange(
        data_model_id=uuid4(),
        user_id=uuid4(),
        base_dbml=SIMPLE_DBML,
        proposed_dbml=SIMPLE_DBML,
        status=DataModelChangeStatus.REJECTED,
    )

    model = DataModelChangeMapper.to_model(entity)
    restored = DataModelChangeMapper.to_domain(model)

    assert model.status == "REJECTED"
    assert restored.status is DataModelChangeStatus.REJECTED
    assert restored.data_model_id == entity.data_model_id
    assert restored.user_id == entity.user_id


def test_data_model_mapper_preserves_revisions_and_attributes() -> None:
    """DataModel mapper round-trip giữ nguyên revisions và không có trường None."""
    entity = DataModel(
        project_id=uuid4(),
        dbml=SIMPLE_DBML,
        revision=2,
        generated_from_requirement_revision=3,
        generated_from_source_revision=4,
    )

    model = DataModelMapper.to_model(entity)
    restored = DataModelMapper.to_domain(model)

    assert model.dbml == SIMPLE_DBML
    assert model.revision == 2
    assert model.generated_from_requirement_revision == 3
    assert model.generated_from_source_revision == 4
    assert restored.project_id == entity.project_id
    assert restored.dbml == SIMPLE_DBML
    assert restored.revision == 2
    assert restored.generated_from_requirement_revision == 3
    assert restored.generated_from_source_revision == 4
