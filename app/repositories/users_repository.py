from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User
from app.repositories.sqlalchemy_repository import SqlAlchemyRepository
from app.schemas.user import UserInDB, UserUpdate


class UserRepository(SqlAlchemyRepository[User, UserInDB, UserUpdate]):
    async def exists(self, session: AsyncSession, **filters) -> bool:
        from sqlalchemy import exists

        stmt = select(
            exists().where(*[getattr(self.model, k) == v for k, v in filters.items()])
        )
        result = await session.execute(stmt)
        return bool(result.scalar())

    async def find_with_roles(self, session: AsyncSession, **filters) -> Optional[User]:
        from sqlalchemy.orm import joinedload

        stmt = select(self.model).options(joinedload(User.roles)).filter_by(**filters)
        result = await session.execute(stmt)
        return result.unique().scalar_one_or_none()
