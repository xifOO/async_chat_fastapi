from app.models.models import Permission
from app.repositories.sqlalchemy_repository import SqlAlchemyRepository
from app.schemas.permission import PermissionCreate, PermissionUpdate


class PermissionRepository(
    SqlAlchemyRepository[Permission, PermissionCreate, PermissionUpdate]
): ...
