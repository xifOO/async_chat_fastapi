from typing import List
from fastapi import HTTPException

from app.db.postgres import postgres_db
from app.models.models import User
from app.repositories.users_repository import UserRepository
from app.schemas.user import UserCreate, UserInDB, UserResponse, UserSchema
from app.security import get_password_hash, verify_password
from app.services._service import BaseService


class UserService(BaseService):
    def __init__(self) -> None:
        self.repository = UserRepository(User)
        self.response_schema = UserResponse
        self.db_session_factory = postgres_db

    async def register_user(self, user_data: UserCreate) -> UserResponse:
        async with self.db_session_factory() as session:
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
            return self.response_schema.model_validate(user)

    async def authenticate_user(self, username: str, password: str) -> UserResponse:
        async with self.db_session_factory() as session:
            user = await self.repository.find_one(session, username=username)
            if (
                not user
                or not verify_password(password, user.hashed_password)
                or not user.is_active
            ):
                raise HTTPException(
                    status_code=401,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return self.response_schema.model_validate(user)

    async def get_user_profile(self, user: UserSchema) -> UserResponse:
        async with self.db_session_factory() as session:
            user_profile = await self.repository.find_one(
                session, username=user.username
            )

            if user_profile is None:
                raise HTTPException(status_code=404, detail="User not found")

            return self.response_schema.model_validate(user_profile)

    async def find_in(self, ids: List[int]) -> List[UserResponse]:
        async with self.db_session_factory() as session:
            users = await self.repository.find_in(
                session, ids
            )
            return [self.response_schema.model_validate(record) for record in users]

