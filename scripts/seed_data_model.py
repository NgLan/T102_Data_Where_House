"""Seed dữ liệu mẫu cho luồng Xuất DDL (T-030) và Review đề xuất thay đổi (T-031).

Tạo 1 user + 1 project + 1 data_model (DBML nghiệp vụ Gọi xe) + 1 data_model_change ở trạng thái
PROPOSED, rồi in ra project_id để cấu hình `NEXT_PUBLIC_DEMO_PROJECT_ID` cho Frontend.

Cách chạy (từ thư mục gốc dự án, sau khi `docker compose up -d postgres`):
    python -m scripts.seed_data_model
"""

import asyncio
import sys
from pathlib import Path

BACKEND_PATH = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from uuid import uuid4  # noqa: E402

from sqlalchemy import select  # noqa: E402
from src.common.utils.datetime import utc_now  # noqa: E402
from src.infrastructure.database.init_db import init_db  # noqa: E402
from src.infrastructure.database.models.data_model import DataModelModel  # noqa: E402
from src.infrastructure.database.models.data_model_change import DataModelChangeModel  # noqa: E402
from src.infrastructure.database.models.project import ProjectModel  # noqa: E402
from src.infrastructure.database.models.user import UserModel  # noqa: E402
from src.infrastructure.database.session import AsyncSessionFactory  # noqa: E402

SEED_USERNAME = "demo_architect"
SEED_EMAIL = "demo.architect@ai20k.local"
SEED_PROJECT_NAME = "Ride-hailing Data Warehouse (Demo)"

CURRENT_DBML = """// Định nghĩa Fact & Dimension Tables
Table Fact_Rides {
  ride_key int [pk, increment]
  driver_key int [ref: > Dim_Driver.driver_key]
  customer_key int [ref: > Dim_Customer.customer_key]
  fare_amount decimal(10,2)
  trip_status varchar(20)
  created_at timestamp
}

Table Dim_Driver {
  driver_key int [pk]
  driver_natural_id varchar(50)
  full_name varchar(100)
  vehicle_type varchar(30)
}

Table Dim_Customer {
  customer_key int [pk]
  phone_number varchar(20)
  member_tier varchar(20)
}"""

# Đề xuất của Agent: thêm cột discount_amount + rating, tách Dim_Vehicle khỏi Dim_Driver.
PROPOSED_DBML = """// Định nghĩa Fact & Dimension Tables
Table Fact_Rides {
  ride_key int [pk, increment]
  driver_key int [ref: > Dim_Driver.driver_key]
  customer_key int [ref: > Dim_Customer.customer_key]
  fare_amount decimal(10,2)
  discount_amount decimal(10,2)
  trip_status varchar(20)
  created_at timestamp
}

Table Dim_Driver {
  driver_key int [pk]
  driver_natural_id varchar(50)
  full_name varchar(100)
  vehicle_key int [ref: > Dim_Vehicle.vehicle_key]
  rating decimal(3,2)
}

Table Dim_Vehicle {
  vehicle_key int [pk]
  vehicle_type varchar(30)
  plate_number varchar(20)
}

Table Dim_Customer {
  customer_key int [pk]
  phone_number varchar(20)
  member_tier varchar(20)
}"""


def _audit_fields() -> dict[str, object]:
    """Sinh các trường định danh và mốc thời gian mà tầng Domain chịu trách nhiệm cấp phát."""
    now = utc_now()
    return {"id": uuid4(), "created_at": now, "updated_at": now}


async def _get_or_create_user(session) -> UserModel:
    """Lấy user demo, tạo mới nếu chưa tồn tại."""
    stmt = select(UserModel).where(UserModel.username == SEED_USERNAME)
    user = (await session.execute(stmt)).scalar_one_or_none()
    if user is None:
        user = UserModel(username=SEED_USERNAME, email=SEED_EMAIL, **_audit_fields())
        session.add(user)
        await session.flush()
    return user


async def _get_or_create_project(session, user: UserModel) -> ProjectModel:
    """Lấy project demo, tạo mới nếu chưa tồn tại."""
    stmt = select(ProjectModel).where(ProjectModel.name == SEED_PROJECT_NAME)
    project = (await session.execute(stmt)).scalar_one_or_none()
    if project is None:
        project = ProjectModel(
            name=SEED_PROJECT_NAME,
            description="Dữ liệu mẫu phục vụ demo T-030 (tải file SQL) và T-031 (xem đề xuất).",
            domain="ride-hailing",
            requirement="Thiết kế Data Warehouse chuẩn Kimball cho nghiệp vụ gọi xe.",
            user_id=user.id,
            **_audit_fields(),
        )
        session.add(project)
        await session.flush()
    return project


async def _get_or_create_data_model(session, project: ProjectModel) -> DataModelModel:
    """Lấy mô hình dữ liệu của project, tạo mới nếu chưa tồn tại."""
    stmt = select(DataModelModel).where(DataModelModel.project_id == project.id)
    data_model = (await session.execute(stmt)).scalar_one_or_none()
    if data_model is None:
        data_model = DataModelModel(
            project_id=project.id, dbml=CURRENT_DBML, revision=1, **_audit_fields()
        )
        session.add(data_model)
        await session.flush()
    return data_model


async def _get_or_create_proposal(
    session, data_model: DataModelModel, user: UserModel
) -> DataModelChangeModel:
    """Lấy đề xuất PROPOSED của mô hình dữ liệu, tạo mới nếu chưa tồn tại."""
    stmt = select(DataModelChangeModel).where(
        DataModelChangeModel.data_model_id == data_model.id,
        DataModelChangeModel.status == "PROPOSED",
    )
    change = (await session.execute(stmt)).scalars().first()
    if change is None:
        change = DataModelChangeModel(
            data_model_id=data_model.id,
            user_id=user.id,
            base_revision=data_model.revision,
            proposed_dbml=PROPOSED_DBML,
            status="PROPOSED",
            **_audit_fields(),
        )
        session.add(change)
        await session.flush()
    return change


async def seed() -> None:
    """Khởi tạo schema và seed toàn bộ dữ liệu mẫu."""
    await init_db()

    async with AsyncSessionFactory() as session:
        user = await _get_or_create_user(session)
        project = await _get_or_create_project(session, user)
        data_model = await _get_or_create_data_model(session, project)
        change = await _get_or_create_proposal(session, data_model, user)
        await session.commit()

        print("Seed dữ liệu mẫu thành công!")
        print(f"  project_id     = {project.id}")
        print(f"  data_model_id  = {data_model.id}")
        print(f"  proposal_id    = {change.id}")
        print()
        print("Thêm dòng sau vào frontend/.env.local để giao diện nạp đúng dự án demo:")
        print(f"  NEXT_PUBLIC_DEMO_PROJECT_ID={project.id}")


if __name__ == "__main__":
    asyncio.run(seed())
