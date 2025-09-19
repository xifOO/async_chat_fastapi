from typing import List

from app.db.db import db
from app.models.models import Role
from app.repositories.role_repository import RoleRepository
from app.services._service import BaseService


class RoleService(BaseService):
    def __init__(self) -> None:
        self.repository = RoleRepository(Role)

    async def find_multiple_with_permissions(self, role_names: List[str]):
        async with db.get_db_session() as session:
            return await self.repository.find_multiple_with_permissions(
                session, role_names
            )
