from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from starlette.middleware.authentication import AuthenticationMiddleware

from app.chat.chat import ChatServer
from app.db.mongo import mongo_db
from app.middleware.auth_middleware import JWTAuthMiddleware
from app.routers.auth import router as auth_router
from app.routers.conversation import router as conv_router
from app.routers.messages import router as messages_router
from app.routers.permissions import router as permission_router
from app.routers.roles import router as role_router
from app.routers.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongo_db.write_indexes()
    yield


app = FastAPI(
    title="API Async chat",
    dependencies=[Depends(HTTPBearer(auto_error=False))],
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthenticationMiddleware, backend=JWTAuthMiddleware())

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(role_router)
app.include_router(permission_router)
app.include_router(conv_router)
app.include_router(messages_router)

chat_app = ChatServer().create_app()
app.mount("/ws", chat_app)
