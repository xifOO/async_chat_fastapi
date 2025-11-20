from typing import List, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Role, UserToRole
from app.repositories.sqlalchemy_repository import SqlAlchemyRepository
from app.schemas.role import RoleCreate, RoleUpdate


class RoleRepository(SqlAlchemyRepository[Role, RoleCreate, RoleUpdate]):
    async def find_multiple_with_permissions(
        self, session: AsyncSession, role_names: List[str]
    ) -> Sequence[Role]:
        from sqlalchemy.orm import joinedload

        stmt = (
            select(self.model)
            .options(joinedload(Role.permissions))
            .where(Role.name.in_(role_names))
        )
        result = await session.execute(stmt)
        return result.unique().scalars().all()

    async def assign_to_user(self, session: AsyncSession, role_id: int, user_id: int):
        from sqlalchemy.dialects.postgresql import insert

        stmt = insert(UserToRole).values(role_id=role_id, user_id=user_id)

        stmt = stmt.on_conflict_do_nothing(index_elements=["user_id", "role_id"])

        await session.execute(stmt)
        await session.flush()
