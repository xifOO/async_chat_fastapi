from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Role
from app.repositories.sqlalchemy_repository import SqlAlchemyRepository
from app.schemas.role import RoleCreate, RoleUpdate


class RoleRepository(SqlAlchemyRepository[Role, RoleCreate, RoleUpdate]):
    async def find_multiple_with_permissions(
        self, session: AsyncSession, role_names: List[str]
    ):
        from sqlalchemy.orm import joinedload

        stmt = (
            select(self.model)
            .options(joinedload(Role.permissions))
            .where(Role.name.in_(role_names))
        )
        result = await session.execute(stmt)
        return result.unique().scalars().all()
