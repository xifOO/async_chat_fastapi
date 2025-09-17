from app.models.models import UserToRole
from app.repositories.sqlalchemy_repository import SqlAlchemyRepository
from app.schemas.user_role import UserToRoleCreate, UserToRoleUpdate


class UserToRoleRepository(
    SqlAlchemyRepository[UserToRole, UserToRoleCreate, UserToRoleUpdate]
): ...
