from app.models.models import UserToRole
from app.repositories.user_role_repository import UserToRoleRepository
from app.services._service import BaseService


class UserToRoleService(BaseService):
    def __init__(self) -> None:
        super().__init__(UserToRoleRepository(UserToRole))
