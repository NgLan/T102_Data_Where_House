"""Fixture và bản giả lập dùng chung cho các bài kiểm thử use case Data Model.

Module này không chứa test nào — nó là nơi đặt DBML mẫu và hai repository trong bộ nhớ
được `test_accept_reject_use_cases.py` và `test_ai_revision_use_cases.py` dùng lại.
Tên file giữ tiền tố `test_` vì các module kia đã import theo đường dẫn này.
"""

from src.domain.data_model.entities import DataModel, DataModelChange
from src.domain.data_model.enums import DataModelChangeStatus
from src.domain.data_model.i_data_model_change_repository import IDataModelChangeRepository
from src.domain.data_model.i_data_model_repository import IDataModelRepository
from src.domain.shared.types import EntityID
from typing_extensions import override

# DBML hợp lệ tối thiểu đại diện cho mô hình đang lưu.
SAMPLE_DBML = """Table Dim_Driver {
  driver_key int [pk]
  full_name varchar(100)
  vehicle_type varchar(30)
}"""

# Bản DBML mà AI Agent đề xuất: tách `vehicle_type` sang một bảng dimension riêng.
PROPOSED_DBML = """Table Dim_Driver {
  driver_key int [pk]
  full_name varchar(100)
  vehicle_key int [ref: > Dim_Vehicle.vehicle_key]
}

Table Dim_Vehicle {
  vehicle_key int [pk]
  vehicle_type varchar(30)
}"""


class FakeDataModelRepository(IDataModelRepository):
    """Repository mô hình dữ liệu trong bộ nhớ."""

    def __init__(self, items: list[DataModel] | None = None) -> None:
        """Khởi tạo với danh sách mô hình có sẵn."""
        self.items: list[DataModel] = list(items or [])

    @override
    async def get_by_id(self, entity_id: EntityID) -> DataModel | None:
        """Lấy mô hình theo ID."""
        return next((item for item in self.items if item.id == entity_id), None)

    @override
    async def get_by_project_id(self, project_id: EntityID) -> DataModel | None:
        """Lấy mô hình theo dự án."""
        return next((item for item in self.items if item.project_id == project_id), None)

    @override
    async def save(self, entity: DataModel) -> DataModel:
        """Lưu mới hoặc thay thế mô hình theo ID."""
        self.items = [item for item in self.items if item.id != entity.id]
        self.items.append(entity)
        return entity

    @override
    async def update_if_revision_matches(
        self, entity: DataModel, base_revision: int
    ) -> DataModel | None:
        """Cập nhật khi revision hiện tại vẫn khớp base revision.

        Thực thể đã được tăng revision trước khi gọi vào đây, nên bản ghi hợp lệ có
        `revision == base_revision + 1`.
        """
        if entity.revision != base_revision + 1:
            return None
        return await self.save(entity)

    @override
    async def delete(self, entity_id: EntityID) -> bool:
        """Xoá mô hình theo ID."""
        remaining = [item for item in self.items if item.id != entity_id]
        removed = len(remaining) != len(self.items)
        self.items = remaining
        return removed


class FakeChangeRepository(IDataModelChangeRepository):
    """Repository đề xuất thay đổi trong bộ nhớ."""

    def __init__(self, items: list[DataModelChange] | None = None) -> None:
        """Khởi tạo với danh sách đề xuất có sẵn."""
        self.items: list[DataModelChange] = list(items or [])

    @override
    async def get_by_id(self, entity_id: EntityID) -> DataModelChange | None:
        """Lấy đề xuất theo ID."""
        return next((item for item in self.items if item.id == entity_id), None)

    @override
    async def get_proposed_by_data_model_and_user(
        self,
        data_model_id: EntityID,
        user_id: EntityID,
    ) -> DataModelChange | None:
        """Lấy đề xuất đang chờ theo Data Model và người dùng."""
        return next(
            (
                item
                for item in self.items
                if item.data_model_id == data_model_id
                and item.user_id == user_id
                and item.status is DataModelChangeStatus.PROPOSED
            ),
            None,
        )

    @override
    async def save(self, entity: DataModelChange) -> DataModelChange:
        """Lưu mới hoặc thay thế đề xuất theo ID."""
        self.items = [item for item in self.items if item.id != entity.id]
        self.items.append(entity)
        return entity

    @override
    async def delete(self, entity_id: EntityID) -> bool:
        """Xoá đề xuất theo ID."""
        remaining = [item for item in self.items if item.id != entity_id]
        removed = len(remaining) != len(self.items)
        self.items = remaining
        return removed
