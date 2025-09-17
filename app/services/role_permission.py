from app.models.models import RoleToPermission
from app.repositories.role_permission_repository import RoleToPermissionRepository
from app.services._service import BaseService


class RoleToPermissionService(BaseService):
    def __init__(self) -> None:
        super().__init__(RoleToPermissionRepository(RoleToPermission))
