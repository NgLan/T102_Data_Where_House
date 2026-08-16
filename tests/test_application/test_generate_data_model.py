"""Kiểm thử use case sinh Data Model bằng AI (T-019) và CRUD đầu vào."""

from uuid import uuid4

import pytest
from src.application.data_models.data_model_service import DataModelService
from src.application.data_models.input import GenerateDataModelInput
from src.application.data_sources.data_source_service import DataSourceService
from src.application.data_sources.input import (
    CreateDataSourceInput,
    ListDataSourcesInput,
)
from src.application.requirements.input import (
    CreateRequirementInput,
    ListRequirementsInput,
)
from src.application.requirements.requirement_service import RequirementService
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.data_model.entities import DataModel
from src.domain.data_model.generation import DbmlGenerationResult, IDataModelGenerator
from src.domain.data_source.entities import DataSource
from src.domain.data_source.enums import DataSourceType
from src.domain.data_source.value_objects import (
    ColumnMetadata,
    SchemaMetadata,
    TableMetadata,
)
from src.domain.project.entities import Project
from src.domain.requirement.entities import Requirement
from src.domain.requirement.enums import RequirementPriority, RequirementType

from tests.fakes import (
    FakeAnalyticalRequirementRepository,
    FakeDataModelRepository,
    FakeDataSourceRepository,
    FakeProjectRepository,
    FakeRequirementRepository,
    FakeUnitOfWork,
)

GENERATED_DBML = """Table Dim_Driver {
  driver_key int [pk]
  full_name varchar
}"""


class FakeGenerator(IDataModelGenerator):
    """Pipeline AI giả lập, trả kết quả dựng sẵn và ghi lại tham số nhận được."""

    def __init__(self, result: DbmlGenerationResult | None = None) -> None:
        """Khởi tạo với kết quả muốn trả về."""
        self._result = result or DbmlGenerationResult(
            dbml=GENERATED_DBML,
            summary="Đã thiết kế 1 dimension.",
            analyzed_schema=SchemaMetadata(
                tables=(
                    TableMetadata(
                        name="drivers",
                        columns=(ColumnMetadata(name="id", data_type="int", primary_key=True),),
                    ),
                )
            ),
        )
        self.received_requirements: list[Requirement] = []
        self.received_data_sources: list[DataSource] = []

    async def generate(
        self, requirements: list[Requirement], data_sources: list[DataSource]
    ) -> DbmlGenerationResult:
        """Ghi nhận tham số rồi trả kết quả dựng sẵn."""
        self.received_requirements = requirements
        self.received_data_sources = data_sources
        return self._result


@pytest.fixture
def project() -> Project:
    """Dự án mẫu."""
    return Project(name="Demo", requirement="Thiết kế DWH gọi xe.", user_id=uuid4())


@pytest.fixture
def unit_of_work() -> FakeUnitOfWork:
    """Đơn vị công việc giả lập."""
    return FakeUnitOfWork()


def _build_generate_service(
    project: Project,
    unit_of_work: FakeUnitOfWork,
    requirements: list[Requirement] | None = None,
    data_sources: list[DataSource] | None = None,
    data_models: list[DataModel] | None = None,
    generator: FakeGenerator | None = None,
) -> tuple[DataModelService, FakeDataSourceRepository, FakeAnalyticalRequirementRepository]:
    """Dựng DataModelService đủ phụ thuộc cho use case sinh mô hình bằng AI."""
    data_source_repo = FakeDataSourceRepository(data_sources or [])
    analytical_repo = FakeAnalyticalRequirementRepository([])
    service = DataModelService(
        repository=FakeDataModelRepository(data_models or []),
        unit_of_work=unit_of_work,
        requirement_repository=FakeRequirementRepository(requirements or []),
        data_source_repository=data_source_repo,
        analytical_repository=analytical_repo,
        generator=generator or FakeGenerator(),
    )
    return service, data_source_repo, analytical_repo


# --- T-019: sinh Data Model bằng AI -------------------------------------------


@pytest.mark.asyncio
async def test_generate_creates_data_model_at_revision_one(
    project: Project, unit_of_work: FakeUnitOfWork
) -> None:
    """Dự án chưa có Data Model thì tạo mới ở revision 1."""
    requirement = Requirement(project_id=project.id, title="Doanh thu", description="Xem doanh thu.")
    service, _, _ = _build_generate_service(project, unit_of_work, requirements=[requirement])

    result = await service.generate_data_model(GenerateDataModelInput(project_id=project.id))

    assert result.dbml == GENERATED_DBML
    assert result.revision == 1
    assert result.project_id == project.id
    assert unit_of_work.commit_count == 1


@pytest.mark.asyncio
async def test_generate_updates_existing_data_model(
    project: Project, unit_of_work: FakeUnitOfWork
) -> None:
    """Dự án đã có Data Model thì cập nhật và tăng revision."""
    existing = DataModel(project_id=project.id, dbml="Table Old {\n  id int [pk]\n}", revision=2)
    requirement = Requirement(project_id=project.id, title="Doanh thu", description="Xem doanh thu.")
    service, _, _ = _build_generate_service(
        project, unit_of_work, requirements=[requirement], data_models=[existing]
    )

    result = await service.generate_data_model(GenerateDataModelInput(project_id=project.id))

    assert result.dbml == GENERATED_DBML
    assert result.revision == 3


@pytest.mark.asyncio
async def test_generate_passes_project_inputs_to_pipeline(
    project: Project, unit_of_work: FakeUnitOfWork
) -> None:
    """Pipeline phải nhận đúng yêu cầu và nguồn dữ liệu của dự án."""
    requirement = Requirement(project_id=project.id, title="Doanh thu", description="Xem doanh thu.")
    data_source = DataSource(project_id=project.id, name="rides", location="/data/rides.csv")
    generator = FakeGenerator()
    service, _, _ = _build_generate_service(
        project,
        unit_of_work,
        requirements=[requirement],
        data_sources=[data_source],
        generator=generator,
    )

    await service.generate_data_model(GenerateDataModelInput(project_id=project.id))

    assert [item.title for item in generator.received_requirements] == ["Doanh thu"]
    assert [item.name for item in generator.received_data_sources] == ["rides"]


@pytest.mark.asyncio
async def test_generate_persists_analyzed_schema_into_data_source(
    project: Project, unit_of_work: FakeUnitOfWork
) -> None:
    """Kết quả phân tích của SourceDataAgent được lưu ngược vào nguồn dữ liệu."""
    data_source = DataSource(project_id=project.id, name="rides", location="/data/rides.csv")
    service, data_source_repo, _ = _build_generate_service(
        project, unit_of_work, data_sources=[data_source]
    )

    await service.generate_data_model(GenerateDataModelInput(project_id=project.id))

    saved = await data_source_repo.get_by_id(data_source.id)
    assert saved is not None
    assert saved.schema_metadata is not None
    assert saved.schema_metadata.tables[0].name == "drivers"


@pytest.mark.asyncio
async def test_generate_persists_analytical_requirements(
    project: Project, unit_of_work: FakeUnitOfWork
) -> None:
    """Yêu cầu phân tích do RequirementAgent sinh ra được lưu xuống CSDL."""
    requirement = Requirement(project_id=project.id, title="Doanh thu", description="Xem doanh thu.")
    analytical = AnalyticalRequirement(requirement_id=requirement.id, metric="tổng doanh thu")
    generator = FakeGenerator(
        DbmlGenerationResult(
            dbml=GENERATED_DBML,
            summary="ok",
            analyzed_schema=SchemaMetadata(),
            analytical_requirements=(analytical,),
        )
    )
    service, _, analytical_repo = _build_generate_service(
        project, unit_of_work, requirements=[requirement], generator=generator
    )

    await service.generate_data_model(GenerateDataModelInput(project_id=project.id))

    saved = await analytical_repo.get_by_requirement_id(requirement.id)
    assert len(saved) == 1
    assert saved[0].metric == "tổng doanh thu"


@pytest.mark.asyncio
async def test_generate_rejects_project_without_any_input(
    project: Project, unit_of_work: FakeUnitOfWork
) -> None:
    """Dự án không có yêu cầu lẫn nguồn dữ liệu thì không gọi LLM, báo lỗi ngay."""
    service, _, _ = _build_generate_service(project, unit_of_work)

    with pytest.raises(BusinessException) as exc_info:
        await service.generate_data_model(GenerateDataModelInput(project_id=project.id))

    assert exc_info.value.code == ErrorCode.INVALID_DATA_MODEL
    assert unit_of_work.commit_count == 0


# --- CRUD Requirement ---------------------------------------------------------


@pytest.mark.asyncio
async def test_create_requirement(project: Project, unit_of_work: FakeUnitOfWork) -> None:
    """Tạo yêu cầu nghiệp vụ thành công và chốt giao dịch."""
    service = RequirementService(
        FakeRequirementRepository([]), FakeProjectRepository([project]), unit_of_work
    )

    result = await service.create_requirement(
        CreateRequirementInput(
            project_id=project.id,
            title="Doanh thu theo tài xế",
            description="Cần xem tổng doanh thu từng tài xế theo tháng.",
            type=RequirementType.BUSINESS,
            priority=RequirementPriority.HIGH,
        )
    )

    assert result.title == "Doanh thu theo tài xế"
    assert result.priority is RequirementPriority.HIGH
    assert unit_of_work.commit_count == 1


@pytest.mark.asyncio
async def test_create_requirement_rejects_unknown_project(
    unit_of_work: FakeUnitOfWork,
) -> None:
    """Tạo yêu cầu cho dự án không tồn tại phải trả lỗi PROJECT_NOT_FOUND."""
    service = RequirementService(
        FakeRequirementRepository([]), FakeProjectRepository([]), unit_of_work
    )

    with pytest.raises(BusinessException) as exc_info:
        await service.create_requirement(
            CreateRequirementInput(
                project_id=uuid4(),
                title="X",
                description="Y",
                type=RequirementType.BUSINESS,
                priority=RequirementPriority.MEDIUM,
            )
        )

    assert exc_info.value.code == ErrorCode.PROJECT_NOT_FOUND


@pytest.mark.asyncio
async def test_list_requirements_only_returns_project_items(
    project: Project, unit_of_work: FakeUnitOfWork
) -> None:
    """Chỉ trả về yêu cầu thuộc đúng dự án được hỏi."""
    mine = Requirement(project_id=project.id, title="Của tôi", description="mô tả")
    other = Requirement(project_id=uuid4(), title="Của dự án khác", description="mô tả")
    service = RequirementService(
        FakeRequirementRepository([mine, other]), FakeProjectRepository([project]), unit_of_work
    )

    results = await service.list_requirements(ListRequirementsInput(project_id=project.id))

    assert [item.title for item in results] == ["Của tôi"]


# --- CRUD Data Source ---------------------------------------------------------


@pytest.mark.asyncio
async def test_create_data_source(project: Project, unit_of_work: FakeUnitOfWork) -> None:
    """Đăng ký nguồn dữ liệu thành công, schema_metadata ban đầu để trống."""
    service = DataSourceService(
        FakeDataSourceRepository([]), FakeProjectRepository([project]), unit_of_work
    )

    result = await service.create_data_source(
        CreateDataSourceInput(
            project_id=project.id,
            name="rides_export",
            location="/data/rides.csv",
            type=DataSourceType.CSV,
            description="Bảng chuyến đi.",
        )
    )

    assert result.name == "rides_export"
    assert result.schema_metadata is None
    assert unit_of_work.commit_count == 1


@pytest.mark.asyncio
async def test_list_data_sources_only_returns_project_items(
    project: Project, unit_of_work: FakeUnitOfWork
) -> None:
    """Chỉ trả về nguồn dữ liệu thuộc đúng dự án được hỏi."""
    mine = DataSource(project_id=project.id, name="mine", location="/a.csv")
    other = DataSource(project_id=uuid4(), name="other", location="/b.csv")
    service = DataSourceService(
        FakeDataSourceRepository([mine, other]), FakeProjectRepository([project]), unit_of_work
    )

    results = await service.list_data_sources(ListDataSourcesInput(project_id=project.id))

    assert [item.name for item in results] == ["mine"]
