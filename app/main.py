from fastapi import Depends, FastAPI
from fastapi.security import HTTPBearer
from starlette.middleware.authentication import AuthenticationMiddleware

from app.middleware.auth_middleware import JWTAuthMiddleware
from app.routers.auth import router as auth_router
from app.routers.permission import router as permission_router
from app.routers.role import router as role_router

app = FastAPI(
    title="API Async chat", dependencies=[Depends(HTTPBearer(auto_error=False))]
)

app.include_router(auth_router)
app.include_router(role_router)
app.include_router(permission_router)


app.add_middleware(AuthenticationMiddleware, backend=JWTAuthMiddleware())
