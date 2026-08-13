"""Unit tests chi tiết cho toàn bộ các Domain ↔ Persistence Mappers."""

from datetime import UTC, datetime
from uuid import uuid4

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
from src.domain.user.entities import User
from src.domain.user.value_objects import Email
from src.infrastructure.database.mappers import (
    DataSourceMapper,
    ProjectMapper,
    SessionEventMapper,
    UserMapper,
)


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
    assert model.email == "john@example.com"
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
