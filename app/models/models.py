from typing import Text

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import Base
from app.models.mixins import IntegerIDMixin, TimeStampMixin


class UserToRole(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)


class RoleToPermission(Base):
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id"), primary_key=True
    )
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)


class User(IntegerIDMixin, TimeStampMixin, Base):
    username: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)

    is_active: Mapped[bool] = mapped_column(default=True)

    roles = relationship(
        "Role", secondary=UserToRole.__table__, back_populates="users", lazy="selectin"
    )


class Role(IntegerIDMixin, Base):
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[Text]

    permissions = relationship(
        "Permission", secondary=RoleToPermission.__table__, back_populates="roles"
    )

    users = relationship("User", secondary=UserToRole.__table__, back_populates="roles")


class Permission(IntegerIDMixin, Base):
    name: Mapped[str] = mapped_column(unique=True)
    resource: Mapped[str]
    action: Mapped[str]
    description: Mapped[Text] = mapped_column(nullable=True)

    roles = relationship(
        "Role", secondary=RoleToPermission.__table__, back_populates="permissions"
    )
