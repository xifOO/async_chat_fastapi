from typing import List, Sequence

from app.db.postgres import postgres_db
from app.models.models import Role
from app.repositories.role_repository import RoleRepository
from app.schemas.role import RoleResponse
from app.services._service import BaseService


class RoleService(BaseService):
    def __init__(self) -> None:
        self.repository = RoleRepository(Role)
        self.response_schema = RoleResponse

    async def find_multiple_with_permissions(
        self, role_names: List[str]
    ) -> Sequence[Role]:
        async with postgres_db.get_db_session() as session:
            records = await self.repository.find_multiple_with_permissions(
                session, role_names
            )
            return records

    async def assign_to_user(self, role_id: int, user_id: int) -> None:
        async with postgres_db.get_db_session() as session:
            await self.repository.assign_to_user(session, role_id, user_id)
