"""Dependency Injection dựng các Use Case Service cho tầng Presentation."""

from typing import Annotated

from fastapi import Depends
from src.application.data_models.generate_ddl import GenerateDdlService
from src.application.data_models.get_change_proposal import GetChangeProposalService
from src.application.data_models.get_data_model import GetDataModelService
from src.application.data_models.i_generate_ddl_service import IGenerateDdlService
from src.application.data_models.i_get_change_proposal_service import (
    IGetChangeProposalService,
)
from src.application.data_models.i_get_data_model_service import IGetDataModelService
from src.application.data_models.i_list_change_proposals_service import (
    IListChangeProposalsService,
)
from src.application.data_models.list_change_proposals import ListChangeProposalsService
from src.domain.data_model.codegen import IDdlGenerator
from src.domain.data_model.repository import (
    IDataModelChangeRepository,
    IDataModelRepository,
)
from src.infrastructure.codegen.ddl_generator import DbmlDdlGenerator
from src.infrastructure.repositories.postgres_data_model_change_repository import (
    PostgresDataModelChangeRepository,
)
from src.infrastructure.repositories.postgres_data_model_repository import (
    PostgresDataModelRepository,
)
from src.presentation.dependencies.database import DbSession


def get_data_model_repository(session: DbSession) -> IDataModelRepository:
    """Cấp phát repository mô hình dữ liệu gắn với phiên CSDL của request."""
    return PostgresDataModelRepository(session)


def get_data_model_change_repository(session: DbSession) -> IDataModelChangeRepository:
    """Cấp phát repository đề xuất thay đổi gắn với phiên CSDL của request."""
    return PostgresDataModelChangeRepository(session)


def get_ddl_generator() -> IDdlGenerator:
    """Cấp phát bộ sinh mã DDL từ DBML (không phụ thuộc trạng thái request)."""
    return DbmlDdlGenerator()


DataModelRepository = Annotated[IDataModelRepository, Depends(get_data_model_repository)]
ChangeRepository = Annotated[
    IDataModelChangeRepository, Depends(get_data_model_change_repository)
]
DdlGenerator = Annotated[IDdlGenerator, Depends(get_ddl_generator)]


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


GetDataModelUseCase = Annotated[IGetDataModelService, Depends(get_data_model_service)]
GenerateDdlUseCase = Annotated[IGenerateDdlService, Depends(get_generate_ddl_service)]
ListChangeProposalsUseCase = Annotated[
    IListChangeProposalsService, Depends(get_list_change_proposals_service)
]
GetChangeProposalUseCase = Annotated[
    IGetChangeProposalService, Depends(get_change_proposal_service)
]
