"""Base model class cho các ORM models trong SQLAlchemy 2.0."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from src.common.utils.datetime import utc_now


class Base(DeclarativeBase):
    """Lớp cơ sở cho tất cả các bảng dữ liệu SQLAlchemy (Domain sở hữu state id, created_at, updated_at).

    Hai cột thời gian có cả `default` (phía Python) lẫn `server_default` (phía CSDL). Tầng
    Domain vẫn làm chủ hai mốc này trong luồng nghiệp vụ; đây chỉ là lưới an toàn cho các
    đường ghi kỹ thuật như seed dữ liệu khởi tạo — trước đây `init_db` dựng `UserModel`
    không kèm timestamp nên ném `NotNullViolationError` ở mọi lần khởi động, và lỗi bị
    nuốt thành một dòng warning.

    Cần `default` phía Python chứ không chỉ `server_default`: `Base.metadata.create_all`
    không ALTER bảng đã tồn tại, nên các CSDL đang chạy vẫn giữ cột NOT NULL không default.
    Giá trị Python được điền ngay trong câu INSERT nên đúng cho cả bảng cũ lẫn bảng mới.
    """

    id: Mapped[UUID] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
        server_default=func.now(),
    )
