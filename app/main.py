from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from starlette.middleware.authentication import AuthenticationMiddleware

from app.dependencies import redis_manager
from app.chat.chat import ChatServer
from app.config import settings
from app.middleware.auth_middleware import JWTAuthMiddleware
from app.middleware.context import ContextMiddleware
from app.routers.auth import router as auth_router
from app.routers.conversation import router as conv_router
from app.routers.messages import router as messages_router
from app.routers.permissions import router as permission_router
from app.routers.roles import router as role_router
from app.routers.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()
    try:
        yield
    finally:
        await redis_manager.disconnect()

app = FastAPI(
    title="API Async chat", 
    lifespan=lifespan,
    dependencies=[Depends(HTTPBearer(auto_error=False))]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.origins,
    allow_credentials=settings.cors.credentials,
    allow_methods=settings.cors.methods,
    allow_headers=settings.cors.headers,
)

app.add_middleware(AuthenticationMiddleware, backend=JWTAuthMiddleware())
app.add_middleware(ContextMiddleware)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(role_router)
app.include_router(permission_router)
app.include_router(conv_router)
app.include_router(messages_router)

chat_app = ChatServer(redis=redis_manager).create_app()
app.mount("/ws", chat_app)
