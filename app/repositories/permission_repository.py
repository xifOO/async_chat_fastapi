from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Permission, RoleToPermission
from app.repositories.sqlalchemy_repository import SqlAlchemyRepository
from app.schemas.permission import PermissionCreate, PermissionUpdate


class PermissionRepository(
    SqlAlchemyRepository[Permission, PermissionCreate, PermissionUpdate]
):
    async def assign_to_role(
        self, session: AsyncSession, permission_id: int, role_id: int
    ):
        from sqlalchemy.dialects.postgresql import insert

        stmt = insert(RoleToPermission).values(
            permission_id=permission_id, role_id=role_id
        )

        stmt = stmt.on_conflict_do_nothing(index_elements=["role_id", "permission_id"])

        await session.execute(stmt)
        await session.flush()
