from app.models.models import Role
from app.schemas.role import RoleCreate
from app.services._service import BaseService
from app.uow.uow import AbstractUnitOfWork


class RoleService(BaseService):
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    async def create_role(self, data: RoleCreate) -> Role:
        async with self.uow:
            role = await self.uow.roles.create(data)
            return role
    