"""Unit tests cho UC5.1.3 chỉnh sửa Data Model trực quan."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_models.data_model_service import DataModelService
from src.application.data_models.i_data_model_service import IDataModelDdlGenerator
from src.application.data_models.input import ChangeProposalIdInput, UpdateDataModelInput
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_model.entities import DataModel, DataModelChange
from src.domain.data_model.enums import DataModelChangeStatus
from src.domain.data_model.i_data_model_repository import IDataModelRepository
from src.domain.project.entities import Project
from src.domain.sandbox.enums import SandboxDbType
from src.infrastructure.validation.dbml_validation_engine import DbmlValidationEngine

from tests.fakes import FakeProjectMemberRepository, FakeProjectRepository
from tests.test_application.test_data_model_use_cases import (
    FakeChangeRepository,
    FakeDataModelRepository,
)


class FakeDdlGenerator(IDataModelDdlGenerator):
    """Test double không được gọi trong nhóm test chỉnh sửa Data Model."""

    def generate_ddl(self, dbml: str, db_type: SandboxDbType) -> str:
        del db_type
        return dbml


def test_data_model_accepts_structured_dbml() -> None:
    """DBML hợp lệ hỗ trợ composite PK, default, unique và note."""
    dbml = r"""
    Table order_items {
      order_id uuid [pk, not null]
      product_id uuid [pk, not null]
      quantity integer [not null, default: 1]
      description varchar(255) [unique, note: 'Mô tả']
      owner_name varchar(255) [note: 'O\'Brien']
    }
    """

    data_model = DataModel(project_id=uuid4(), dbml=dbml)

    assert data_model.revision == 1


def test_data_model_accepts_custom_dbml_data_type() -> None:
    """DBML cho phép custom type thay vì áp một whitelist theo database cụ thể."""
    data_model = DataModel(
        project_id=uuid4(),
        dbml="Table users {\n amount money_domain\n}",
    )

    assert data_model.revision == 1


@pytest.mark.parametrize(
    "dbml",
    [
        "đây chỉ là một chuỗi văn bản rác",
        "Table users {\n amount integer [default:]\n}",
        "Table users {\n id uuid\n",
        "Table {\n id uuid\n}",
    ],
)
def test_validation_engine_rejects_invalid_dbml(dbml: str) -> None:
    """Validation adapter từ chối DBML không thể parse trước persistence."""
    issues = DbmlValidationEngine().validate(dbml)

    assert any(issue.severity.value == "ERROR" for issue in issues)


def test_validation_engine_rejects_duplicate_columns() -> None:
    """Rule registry phát hiện duplicate column mà parser vẫn chấp nhận."""
    dbml = "Table users {\n id uuid [pk]\n id varchar\n}"

    issues = DbmlValidationEngine().validate(dbml)

    assert any("trùng" in issue.title.lower() for issue in issues)


@pytest.mark.asyncio
async def test_manual_update_changes_snapshot_without_proposal() -> None:
    """Editor lưu trực tiếp snapshot và không tạo Human Review proposal."""
    current = DataModel(project_id=uuid4(), dbml="Table users { id uuid }", revision=3)
    repository = FakeDataModelRepository([current])
    changes = FakeChangeRepository([])
    unit_of_work = AsyncMock(spec=IUnitOfWork)
    service = create_service(current, repository, unit_of_work, changes)
    command = create_command(current, "Table users {\n id uuid [pk]\n}", 3)

    result = await service.update_data_model(command)

    assert result.revision == 4
    assert result.dbml.endswith("}")
    assert current.revision == 4
    assert changes.items == []
    unit_of_work.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_manual_updates_increment_snapshot_revision_each_time() -> None:
    """Mỗi lần lưu editor hợp lệ cập nhật snapshot và tăng revision."""
    current = DataModel(project_id=uuid4(), dbml="Table users { id uuid }", revision=3)
    repository = FakeDataModelRepository([current])
    unit_of_work = AsyncMock(spec=IUnitOfWork)
    change_repository = FakeChangeRepository([])
    service = create_service(current, repository, unit_of_work, change_repository)
    command = create_command(current, "Table users {\n id uuid [pk]\n}", 3)

    first = await service.update_data_model(command)
    second = await service.update_data_model(
        create_command(current, "Table users {\n id uuid [pk, unique]\n}", 4)
    )

    assert first.revision == 4
    assert second.revision == 5
    assert change_repository.items == []
    assert current.revision == 5


@pytest.mark.asyncio
async def test_update_service_rejects_outdated_base_revision() -> None:
    """Revision cũ bị từ chối trước persistence và không ghi đè snapshot mới hơn."""
    current = DataModel(project_id=uuid4(), dbml="Table users { id uuid }", revision=4)
    repository = AsyncMock(spec=IDataModelRepository)
    unit_of_work = AsyncMock(spec=IUnitOfWork)
    repository.get_by_project_id.return_value = current
    service = create_service(current, repository, unit_of_work)
    command = create_command(current, "Table users {\n id uuid [pk]\n}", 3)

    with pytest.raises(BusinessException) as exc_info:
        await service.update_data_model(command)

    assert exc_info.value.code == ErrorCode.DATA_MODEL_REVISION_CONFLICT
    repository.update_if_revision_matches.assert_not_awaited()


@pytest.mark.asyncio
async def test_manual_update_handles_persistence_revision_race() -> None:
    """Concurrent update tại persistence trả revision conflict và không commit."""
    current = DataModel(project_id=uuid4(), dbml="Table users { id uuid }", revision=3)
    repository = AsyncMock(spec=IDataModelRepository)
    repository.get_by_project_id.return_value = current
    repository.update_if_revision_matches.return_value = None
    unit_of_work = AsyncMock(spec=IUnitOfWork)
    service = create_service(current, repository, unit_of_work)

    with pytest.raises(BusinessException) as exc_info:
        await service.update_data_model(
            create_command(current, "Table users {\n id uuid [pk]\n}", 3)
        )

    assert exc_info.value.code is ErrorCode.DATA_MODEL_REVISION_CONFLICT
    unit_of_work.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_accept_proposal_updates_snapshot_and_revision() -> None:
    """Accept hợp lệ áp proposal đúng một lần và tăng revision."""
    project, model, change = _proposal_context(False)
    repositories = FakeDataModelRepository([model]), FakeChangeRepository([change])
    unit_of_work = AsyncMock(spec=IUnitOfWork)
    service = create_service(model, repositories[0], unit_of_work, repositories[1], project)

    result = await service.accept_change_proposal(ChangeProposalIdInput(change.id))

    assert result.revision == 4
    assert model.dbml == change.proposed_dbml
    assert change.status is DataModelChangeStatus.ACCEPTED
    unit_of_work.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_outdated_proposal_is_persisted_as_conflicted() -> None:
    """Base revision lỗi thời chuyển proposal thành CONFLICTED."""
    project, model, change = _proposal_context(True)
    repositories = FakeDataModelRepository([model]), FakeChangeRepository([change])
    unit_of_work = AsyncMock(spec=IUnitOfWork)
    service = create_service(model, repositories[0], unit_of_work, repositories[1], project)

    with pytest.raises(BusinessException) as exc_info:
        await service.accept_change_proposal(ChangeProposalIdInput(change.id))

    assert exc_info.value.code is ErrorCode.DATA_MODEL_CHANGE_OUTDATED
    assert change.status is DataModelChangeStatus.CONFLICTED
    assert model.revision == 3
    unit_of_work.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_analysis_revision_change_does_not_conflict_proposal() -> None:
    """Analysis revision mới không vô hiệu proposal có base revision hợp lệ."""
    project, model, change = _proposal_context(False)
    project.analyzed_requirement_revision = 4
    project.analyzed_source_revision = 6
    repositories = FakeDataModelRepository([model]), FakeChangeRepository([change])
    service = create_service(
        model, repositories[0], AsyncMock(spec=IUnitOfWork), repositories[1], project
    )

    result = await service.accept_change_proposal(ChangeProposalIdInput(change.id))

    assert change.status is DataModelChangeStatus.ACCEPTED
    assert result.is_outdated is False
    assert model.generated_from_requirement_revision == 4
    assert model.generated_from_source_revision == 6


def create_command(data_model: DataModel, dbml: str, base_revision: int) -> UpdateDataModelInput:
    """Tạo command cập nhật hợp lệ cho unit tests."""
    return UpdateDataModelInput(
        project_id=data_model.project_id,
        data_model_id=data_model.id,
        dbml=dbml,
        base_revision=base_revision,
    )


def create_service(
    current: DataModel,
    repository: IDataModelRepository,
    unit_of_work: IUnitOfWork,
    changes: FakeChangeRepository | None = None,
    project: Project | None = None,
) -> DataModelService:
    owner_id = uuid4()
    current_project = project or Project(
        id=current.project_id,
        name="Demo",
        requirement="Design data warehouse",
        user_id=owner_id,
    )
    current_project.user_id = owner_id
    access = ProjectAccessPolicy(
        FakeProjectRepository([current_project]), FakeProjectMemberRepository([]), owner_id
    )
    return DataModelService(
        repository,
        changes or FakeChangeRepository([]),
        DbmlValidationEngine(),
        unit_of_work,
        access,
        FakeDdlGenerator(),
    )


def _proposal_context(outdated: bool) -> tuple[Project, DataModel, DataModelChange]:
    """Tạo snapshot và proposal cho Human Review tests."""
    project_id = uuid4()
    project = Project(
        id=project_id, name="Demo", requirement="Design data warehouse",
        user_id=uuid4(), requirement_revision=3, source_revision=5,
        analyzed_requirement_revision=3, analyzed_source_revision=5,
    )
    model = DataModel(
        project_id=project_id,
        dbml="Table users {\n id uuid [pk]\n}",
        revision=3,
        generated_from_requirement_revision=3,
        generated_from_source_revision=5,
    )
    change = DataModelChange(
        data_model_id=model.id,
        user_id=uuid4(),
        base_revision=2 if outdated else 3,
        proposed_dbml="Table users {\n id uuid [pk]\n email varchar\n}",
    )
    return project, model, change
