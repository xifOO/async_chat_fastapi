from app.models.models import RoleToPermission
from app.repositories.sqlalchemy_repository import SqlAlchemyRepository
from app.schemas.role_permission import RoleToPermissionCreate, RoleToPermissionUpdate


class RoleToPermissionRepository(
    SqlAlchemyRepository[
        RoleToPermission, RoleToPermissionCreate, RoleToPermissionUpdate
    ]
): ...
