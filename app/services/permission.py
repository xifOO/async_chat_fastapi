from app.models.models import Permission
from app.repositories.permission_repository import PermissionRepository
from app.services._service import BaseService


class PermissionService(BaseService):
    def __init__(self) -> None:
        super().__init__(PermissionRepository(Permission))
