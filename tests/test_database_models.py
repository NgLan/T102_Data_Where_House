"""Unit tests cho các SQLAlchemy ORM Models thuộc tầng Infrastructure Database."""

from sqlalchemy.orm import Mapper, class_mapper
from src.infrastructure.database.base import Base
from src.infrastructure.database.models import (
    AnalyticalRequirementModel,
    DataModelChangeModel,
    DataModelModel,
    DataSourceModel,
    ProjectMemberModel,
    ProjectModel,
    ProjectSessionModel,
    RequirementModel,
    SessionEventModel,
    UserModel,
)


def test_all_sqlalchemy_models_mapped_successfully() -> None:
    """Đảm bảo tất cả 10 ORM Models được mapping thành công không có lỗi cấu hình."""
    models = [
        UserModel,
        ProjectModel,
        ProjectMemberModel,
        RequirementModel,
        AnalyticalRequirementModel,
        DataSourceModel,
        ProjectSessionModel,
        SessionEventModel,
        DataModelModel,
        DataModelChangeModel,
    ]

    for model in models:
        mapper: Mapper = class_mapper(model)
        assert mapper is not None
        assert model.__tablename__ is not None


def test_table_names() -> None:
    """Kiểm tra tên bảng khớp chính xác với database.md."""
    assert UserModel.__tablename__ == "users"
    assert ProjectModel.__tablename__ == "projects"
    assert ProjectMemberModel.__tablename__ == "project_members"
    assert RequirementModel.__tablename__ == "requirements"
    assert AnalyticalRequirementModel.__tablename__ == "analytical_requirements"
    assert DataSourceModel.__tablename__ == "data_sources"
    assert ProjectSessionModel.__tablename__ == "project_sessions"
    assert SessionEventModel.__tablename__ == "session_events"
    assert DataModelModel.__tablename__ == "data_models"
    assert DataModelChangeModel.__tablename__ == "data_model_changes"


def test_metadata_tables_count() -> None:
    """Đảm bảo Base.metadata ghi nhận đủ 10 bảng."""
    table_names = set(Base.metadata.tables.keys())
    expected_tables = {
        "users",
        "projects",
        "project_members",
        "requirements",
        "analytical_requirements",
        "data_sources",
        "project_sessions",
        "session_events",
        "data_models",
        "data_model_changes",
    }
    assert expected_tables.issubset(table_names)
