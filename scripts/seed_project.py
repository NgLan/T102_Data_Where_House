"""Seed một user và một project trống để thử pipeline sinh mô hình dữ liệu (T-019).

Yêu cầu nghiệp vụ và nguồn dữ liệu KHÔNG seed ở đây — hãy nạp chúng qua API:
    POST /api/v1/projects/{project_id}/requirements
    POST /api/v1/projects/{project_id}/data-sources

Cách chạy (từ thư mục gốc dự án, sau khi `docker compose up -d postgres`):
    python -m scripts.seed_project
"""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4

BACKEND_PATH = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from sqlalchemy import select  # noqa: E402
from src.common.utils.datetime import utc_now  # noqa: E402
from src.infrastructure.database.init_db import init_db  # noqa: E402
from src.infrastructure.database.models.project import ProjectModel  # noqa: E402
from src.infrastructure.database.models.user import UserModel  # noqa: E402
from src.infrastructure.database.session import get_async_session_factory  # noqa: E402

SEED_USERNAME = "demo_architect"
SEED_EMAIL = "demo.architect@ai20k.local"
SEED_PROJECT_NAME = "Ride-hailing Data Warehouse (Demo)"


def _audit_fields() -> dict[str, object]:
    """Sinh định danh và mốc thời gian mà tầng Domain chịu trách nhiệm cấp phát."""
    now = utc_now()
    return {"id": uuid4(), "created_at": now, "updated_at": now}


async def seed() -> None:
    """Khởi tạo schema và seed user + project."""
    await init_db()

    async with get_async_session_factory()() as session:
        user = (
            await session.execute(
                select(UserModel).where(UserModel.username == SEED_USERNAME)
            )
        ).scalar_one_or_none()
        if user is None:
            user = UserModel(username=SEED_USERNAME, email=SEED_EMAIL, **_audit_fields())
            session.add(user)
            await session.flush()

        project = (
            await session.execute(
                select(ProjectModel).where(ProjectModel.name == SEED_PROJECT_NAME)
            )
        ).scalar_one_or_none()
        if project is None:
            project = ProjectModel(
                name=SEED_PROJECT_NAME,
                description="Dữ liệu mẫu phục vụ thử pipeline 4 agent (T-019).",
                domain="ride-hailing",
                requirement="Thiết kế Data Warehouse chuẩn Kimball cho nghiệp vụ gọi xe.",
                user_id=user.id,
                **_audit_fields(),
            )
            session.add(project)
            await session.flush()

        await session.commit()

        print("Seed thành công!")
        print(f"  project_id = {project.id}")


if __name__ == "__main__":
    asyncio.run(seed())
