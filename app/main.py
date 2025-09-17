from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.role import router as role_router

app = FastAPI(title="API Async chat")

app.include_router(auth_router)
app.include_router(role_router)
