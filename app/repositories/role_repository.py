from app.models.models import Role
from app.repositories.sqlalchemy_repository import SqlAlchemyRepository
from app.schemas.role import RoleCreate, RoleUpdate


class RoleRepository(SqlAlchemyRepository[Role, RoleCreate, RoleUpdate]): ...
        
