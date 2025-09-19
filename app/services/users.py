from fastapi import HTTPException

from app.db.db import db
from app.models.models import User
from app.repositories.users_repository import UserRepository
from app.schemas.user import UserCreate, UserInDB, UserSchema
from app.security import get_password_hash, verify_password
from app.services._service import BaseService


class UserService(BaseService):
    def __init__(self) -> None:
        self.repository = UserRepository(User)

    async def register_user(self, user_data: UserCreate) -> User:
        async with db.get_db_session() as session:
            if await self.repository.exists(session, email=user_data.email):
                raise HTTPException(status_code=400, detail="Email already exists.")

            if await self.repository.exists(session, username=user_data.username):
                raise HTTPException(status_code=400, detail="Username already exists.")

            db_user = UserInDB(
                username=user_data.username,
                email=user_data.email,
                hashed_password=get_password_hash(user_data.password),
            )

            user = await self.repository.create(session, db_user)
            return user

    async def authenticate_user(self, username: str, password: str) -> User:
        async with db.get_db_session() as session:
            user = await self.repository.find_with_roles(session, username=username)
            if not user or not verify_password(password, user.hashed_password) or not user.is_active:
                raise HTTPException(
                    status_code=401,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return user

    async def get_user_profile(self, user: UserSchema) -> User:
        async with db.get_db_session() as session:
            user_profile = await self.repository.find_with_roles(
                session, username=user.username
            )

            if user_profile is None:
                raise HTTPException(status_code=404, detail="User not found")

            return user_profile
