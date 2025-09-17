from app.models.models import UserToRole
from app.schemas.user_role import UserToRoleCreate
from app.services._service import BaseService
from app.uow.uow import AbstractUnitOfWork


class UserToRoleService(BaseService):
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    async def assing_role_to_user(self, data: UserToRoleCreate) -> UserToRole:
        async with self.uow:
            user_to_role = await self.uow.user_to_role.create(data)
            return user_to_role
    