"""Input model cho các thao tác Data Model."""

from dataclasses import dataclass

from src.domain.shared.types import EntityID


@dataclass(frozen=True)
class GetDataModelInput:
    """Dữ liệu đầu vào để lấy Data Model hiện tại của dự án."""

    project_id: EntityID


@dataclass(frozen=True)
class UpdateDataModelInput:
    """Dữ liệu đầu vào để cập nhật Data Model bằng optimistic locking."""

    project_id: EntityID
    data_model_id: EntityID
    dbml: str
    base_revision: int
