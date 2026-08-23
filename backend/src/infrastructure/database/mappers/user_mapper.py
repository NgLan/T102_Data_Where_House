"""Mapper chuyển đổi dữ liệu giữa User Domain Entity và UserModel Persistence."""

from src.domain.user.entities import User
from src.domain.user.value_objects import Email
from src.infrastructure.database.models.user import UserModel


class UserMapper:
    """Mapper thực hiện chuyển đổi giữa User Entity và UserModel."""

    @staticmethod
    def to_domain(model: UserModel) -> User:
        """Chuyển đổi từ UserModel (Persistence) sang User (Domain Entity)."""
        return User(
            id=model.id,
            username=model.username,
            email=Email(value=model.email),
            password_hash=model.password_hash,
            full_name=model.full_name,
            is_active=model.is_active is True,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: User) -> UserModel:
        """Chuyển đổi từ User (Domain Entity) sang UserModel (Persistence)."""
        return UserModel(
            id=entity.id,
            username=entity.username,
            email=entity.email.value,
            password_hash=entity.password_hash,
            full_name=entity.full_name,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def update_model(model: UserModel, entity: User) -> UserModel:
        """Cập nhật dữ liệu từ User Entity sang UserModel đã tồn tại."""
        model.username = entity.username
        model.email = entity.email.value
        model.password_hash = entity.password_hash
        model.full_name = entity.full_name
        model.is_active = entity.is_active
        model.updated_at = entity.updated_at
        return model
