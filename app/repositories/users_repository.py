from typing import List, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User
from app.repositories.sqlalchemy_repository import SqlAlchemyRepository
from app.schemas.user import UserInDB, UserUpdate


class UserRepository(SqlAlchemyRepository[User, UserInDB, UserUpdate]):
    async def find_in(self, session: AsyncSession, ids: List[int]) -> Sequence[User]:
        from sqlalchemy import select

        stmt = select(self.model).where(self.model.id.in_(ids))
        result = await session.execute(stmt)
        return result.scalars().all()
