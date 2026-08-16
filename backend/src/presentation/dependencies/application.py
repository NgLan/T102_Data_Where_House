"""Dependency Injection dựng các Use Case Service cho tầng Presentation."""

from typing import Annotated

from config import get_settings
from fastapi import Depends
from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_models.accept_change_proposal import AcceptChangeProposalService
from src.application.data_models.create_change_proposal import CreateChangeProposalService
from src.application.data_models.generate_ddl import GenerateDdlService
from src.application.data_models.get_change_proposal import GetChangeProposalService
from src.application.data_models.get_data_model import GetDataModelService
from src.application.data_models.i_accept_change_proposal_service import (
    IAcceptChangeProposalService,
)
from src.application.data_models.i_create_change_proposal_service import (
    ICreateChangeProposalService,
)
from src.application.data_models.i_generate_ddl_service import IGenerateDdlService
from src.application.data_models.i_get_change_proposal_service import (
    IGetChangeProposalService,
)
from src.application.data_models.i_get_data_model_service import IGetDataModelService
from src.application.data_models.i_list_change_proposals_service import (
    IListChangeProposalsService,
)
from src.application.data_models.i_reject_change_proposal_service import (
    IRejectChangeProposalService,
)
from src.application.data_models.list_change_proposals import ListChangeProposalsService
from src.application.data_models.reject_change_proposal import RejectChangeProposalService
from src.domain.data_model.codegen import IDdlGenerator
from src.domain.data_model.repository import (
    IDataModelChangeRepository,
    IDataModelRepository,
)
from src.domain.data_model.revision import IDataModelReviser
from src.domain.project.repository import IProjectRepository
from src.infrastructure.agents.data_model_reviser import LangGraphDataModelReviser
from src.infrastructure.codegen.ddl_generator import DbmlDdlGenerator
from src.infrastructure.llm.factory import build_chat_model
from src.infrastructure.repositories.postgres_data_model_change_repository import (
    PostgresDataModelChangeRepository,
)
from src.infrastructure.repositories.postgres_data_model_repository import (
    PostgresDataModelRepository,
)
from src.infrastructure.repositories.postgres_project_repository import (
    PostgresProjectRepository,
)
from src.infrastructure.security.pii_guard import PiiGuard
from src.infrastructure.transaction.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from src.presentation.dependencies.database import DbSession


def get_data_model_repository(session: DbSession) -> IDataModelRepository:
    """Cấp phát repository mô hình dữ liệu gắn với phiên CSDL của request."""
    return PostgresDataModelRepository(session)


def get_data_model_change_repository(session: DbSession) -> IDataModelChangeRepository:
    """Cấp phát repository đề xuất thay đổi gắn với phiên CSDL của request."""
    return PostgresDataModelChangeRepository(session)


def get_project_repository(session: DbSession) -> IProjectRepository:
    """Cấp phát repository dự án gắn với phiên CSDL của request."""
    return PostgresProjectRepository(session)


def get_ddl_generator() -> IDdlGenerator:
    """Cấp phát bộ sinh mã DDL từ DBML (không phụ thuộc trạng thái request)."""
    return DbmlDdlGenerator()


def get_pii_guard() -> PiiGuard:
    """Cấp phát bộ che thông tin cá nhân đặt giữa Agent và LLM API (FR6.2)."""
    return PiiGuard(enabled=get_settings().pii_masking_enabled)


def get_data_model_reviser(pii_guard: Annotated[PiiGuard, Depends(get_pii_guard)]) -> IDataModelReviser:
    """Cấp phát bộ chỉnh sửa mô hình dữ liệu bằng AI (Agent điều phối + DWDesignAgent)."""
    return LangGraphDataModelReviser(build_chat_model(), pii_guard)


def get_unit_of_work(session: DbSession) -> IUnitOfWork:
    """Cấp phát đơn vị công việc giao dịch gắn với phiên CSDL của request.

    Dùng chung đúng một AsyncSession với các repository nhờ cơ chế cache dependency của
    FastAPI, nhờ đó mọi thao tác ghi trong một request nằm trong cùng một giao dịch.
    """
    return SqlAlchemyUnitOfWork(session)


DataModelRepository = Annotated[IDataModelRepository, Depends(get_data_model_repository)]
ChangeRepository = Annotated[
    IDataModelChangeRepository, Depends(get_data_model_change_repository)
]
ProjectRepository = Annotated[IProjectRepository, Depends(get_project_repository)]
DdlGenerator = Annotated[IDdlGenerator, Depends(get_ddl_generator)]
DataModelReviser = Annotated[IDataModelReviser, Depends(get_data_model_reviser)]
UnitOfWork = Annotated[IUnitOfWork, Depends(get_unit_of_work)]


def get_data_model_service(repository: DataModelRepository) -> IGetDataModelService:
    """Cấp phát use case truy vấn mô hình dữ liệu theo dự án."""
    return GetDataModelService(repository)


def get_generate_ddl_service(
    repository: DataModelRepository,
    generator: DdlGenerator,
) -> IGenerateDdlService:
    """Cấp phát use case sinh mã DDL từ mô hình dữ liệu."""
    return GenerateDdlService(repository, generator)


def get_list_change_proposals_service(
    repository: DataModelRepository,
    change_repository: ChangeRepository,
) -> IListChangeProposalsService:
    """Cấp phát use case liệt kê đề xuất thay đổi của một mô hình dữ liệu."""
    return ListChangeProposalsService(repository, change_repository)


def get_change_proposal_service(
    repository: DataModelRepository,
    change_repository: ChangeRepository,
) -> IGetChangeProposalService:
    """Cấp phát use case xem chi tiết một đề xuất thay đổi."""
    return GetChangeProposalService(repository, change_repository)


def get_create_change_proposal_service(
    repository: DataModelRepository,
    change_repository: ChangeRepository,
    reviser: DataModelReviser,
    project_repository: ProjectRepository,
    unit_of_work: UnitOfWork,
) -> ICreateChangeProposalService:
    """Cấp phát use case nhờ AI chỉnh sửa mô hình dữ liệu và tạo đề xuất (T-024)."""
    return CreateChangeProposalService(
        repository, change_repository, reviser, project_repository, unit_of_work
    )


def get_accept_change_proposal_service(
    repository: DataModelRepository,
    change_repository: ChangeRepository,
    unit_of_work: UnitOfWork,
) -> IAcceptChangeProposalService:
    """Cấp phát use case chấp nhận và áp dụng đề xuất thay đổi (T-032)."""
    return AcceptChangeProposalService(repository, change_repository, unit_of_work)


def get_reject_change_proposal_service(
    change_repository: ChangeRepository,
    unit_of_work: UnitOfWork,
) -> IRejectChangeProposalService:
    """Cấp phát use case từ chối đề xuất thay đổi (T-033)."""
    return RejectChangeProposalService(change_repository, unit_of_work)


GetDataModelUseCase = Annotated[IGetDataModelService, Depends(get_data_model_service)]
GenerateDdlUseCase = Annotated[IGenerateDdlService, Depends(get_generate_ddl_service)]
ListChangeProposalsUseCase = Annotated[
    IListChangeProposalsService, Depends(get_list_change_proposals_service)
]
GetChangeProposalUseCase = Annotated[
    IGetChangeProposalService, Depends(get_change_proposal_service)
]
CreateChangeProposalUseCase = Annotated[
    ICreateChangeProposalService, Depends(get_create_change_proposal_service)
]
AcceptChangeProposalUseCase = Annotated[
    IAcceptChangeProposalService, Depends(get_accept_change_proposal_service)
]
RejectChangeProposalUseCase = Annotated[
    IRejectChangeProposalService, Depends(get_reject_change_proposal_service)
]
