import uuid
from typing import Text

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import Base
from app.models.mixins import IntegerIDMixin, TimeStampMixin, UUIDMixin


class UserConversation(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id"), primary_key=True
    )


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

    messages = relationship("Message", back_populates="author")

    conversation = relationship(
        "Conversation",
        secondary=UserConversation.__table__,
        back_populates="participants",
    )

    roles = relationship("Role", secondary=UserToRole.__table__, back_populates="users")


class Conversation(UUIDMixin, TimeStampMixin, Base):
    topic: Mapped[str]

    messages = relationship("Message", back_populates="conversation")
    participants = relationship(
        "User", secondary=UserConversation.__table__, back_populates="conversation"
    )


class Message(UUIDMixin, TimeStampMixin, Base):
    body: Mapped[Text]

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversations.id"))

    author = relationship("User", back_populates="messages")
    conversation = relationship("Conversation", back_populates="messages")


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
    description: Mapped[Text]

    roles = relationship(
        "Role", secondary=RoleToPermission.__table__, back_populates="permissions"
    )
