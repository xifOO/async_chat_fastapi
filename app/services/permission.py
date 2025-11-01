import asyncpg
from sqlalchemy.exc import IntegrityError

from app.db.postgres import postgres_db
from app.exceptions import RecordAlreadyExists, RecordNotFound
from app.models.models import Permission
from app.repositories.permission_repository import PermissionRepository
from app.schemas.permission import PermissionResponse
from app.services._service import BaseService


class PermissionService(BaseService):
    def __init__(self) -> None:
        self.repository = PermissionRepository(Permission)
        self.response_schema = PermissionResponse
        self.db_session_factory = postgres_db

    async def assing_to_role(self, permission_id: int, role_id: int) -> None:
        async with self.db_session_factory() as session:
            try:
                await self.repository.assign_to_role(session, permission_id, role_id)
            except IntegrityError as e:
                if isinstance(e.orig, asyncpg.ForeignKeyViolationError):
                    raise RecordNotFound(
                        detail=f"Role {role_id} or Permission {permission_id} not found"
                    )
                else:
                    raise RecordAlreadyExists(
                        detail=f"Role {role_id} already has permission {permission_id}"
                    )
