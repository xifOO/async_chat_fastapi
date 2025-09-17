from app.models.models import Role
from app.repositories.role_repository import RoleRepository
from app.services._service import BaseService


class RoleService(BaseService):
    def __init__(self) -> None:
        super().__init__(RoleRepository(Role))
