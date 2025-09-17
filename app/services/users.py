from fastapi import HTTPException

from app.models.models import User
from app.schemas.user import UserCreate, UserInDB, UserSchema
from app.security import get_password_hash, verify_password
from app.services._service import BaseService
from app.uow.uow import AbstractUnitOfWork


class UserService(BaseService):
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    async def register_user(self, user_data: UserCreate) -> User:
        async with self.uow:
            if await self.uow.users.exists(email=user_data.email):
                raise HTTPException(status_code=400, detail="Email already exists.")

            if await self.uow.users.exists(username=user_data.username):
                raise HTTPException(status_code=400, detail="Username already exists.")

            db_user = UserInDB(
                username=user_data.username,
                email=user_data.email,
                hashed_password=get_password_hash(user_data.password),
            )

            user = await self.uow.users.create(db_user)
            return user

    async def authenticate_user(self, username: str, password: str) -> User:
        async with self.uow:
            user = await self.uow.users.find_with_roles(username=username)
            if not user or not verify_password(password, user.hashed_password):
                raise HTTPException(
                    status_code=401,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return user

    async def get_user_profile(self, user: UserSchema) -> User:
        async with self.uow:
            user_profile = await self.uow.users.find_with_roles(username=user.username)

            if user_profile is None:
                raise HTTPException(status_code=404, detail="User not found")

            return user_profile
