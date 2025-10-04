from app.models.models import User
from app.repositories.sqlalchemy_repository import SqlAlchemyRepository
from app.schemas.user import UserInDB, UserUpdate


class UserRepository(SqlAlchemyRepository[User, UserInDB, UserUpdate]): ...
