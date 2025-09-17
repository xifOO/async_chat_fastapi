from abc import ABC, abstractmethod
from typing import Callable, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Role, User, UserToRole
from app.repositories.role_repository import RoleRepository
from app.repositories.user_role_repository import UserToRoleRepository
from app.repositories.users_repository import UserRepository


class AbstractUnitOfWork(ABC):
    @abstractmethod
    async def __aenter__(self) -> "AbstractUnitOfWork": ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb): ...

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...

    @property
    @abstractmethod
    def users(self) -> UserRepository: ...

    @property
    @abstractmethod
    def roles(self) -> RoleRepository: ...

    @property
    @abstractmethod
    def user_to_role(self) -> UserToRoleRepository: ...


class UnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory: Callable[[], AsyncSession]) -> None:
        self._session_factory = session_factory
        self.session: Optional[AsyncSession] = None
        self._users: Optional[UserRepository] = None
        self._roles: Optional[RoleRepository] = None
        self._user_to_role: Optional[UserToRoleRepository] = None

    async def __aenter__(self) -> "UnitOfWork":
        self.session = self._session_factory()
        self._users = UserRepository(User, self.session)
        self._roles = RoleRepository(Role, self.session)
        self._user_to_role = UserToRoleRepository(UserToRole, self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if not self.session:
            return

        try:
            if exc_type:
                await self.rollback()
            else:
                await self.commit()
        finally:
            await self.session.close()

    async def commit(self):
        if self.session:
            await self.session.commit()

    async def rollback(self):
        if self.session:
            await self.session.rollback()

    @property
    def users(self) -> UserRepository:
        if self._users is None:
            raise RuntimeError("Use async context manager.")
        return self._users

    @property
    def roles(self) -> RoleRepository:
        if self._roles is None:
            raise RuntimeError("Use async context manager.")
        return self._roles

    @property
    def user_to_role(self) -> UserToRoleRepository:
        if self._user_to_role is None:
            raise RuntimeError("Use async context manager.")
        return self._user_to_role