import uuid
from httpx import ASGITransport, AsyncClient
from starlette.authentication import AuthCredentials
from app.schemas.user import UserSchema
from app.middleware.auth_middleware import _AuthenticatedUser, JWTAuthMiddleware
import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def async_client(test_db, monkeypatch):
    from app.main import app
    from app.db.db import db 
    
    monkeypatch.setattr(db, "get_db_session", test_db.get_db_session)
    
    async with AsyncClient(transport=ASGITransport(app=app), 
                         base_url="http://test") as client:
        yield client


@pytest.fixture
def auth_patch(monkeypatch):
    def _patch_user(roles):  
        mock_user = UserSchema(
            id=666,
            username="mock_user",
            email="mock@example.com",
            roles=roles
        )

        async def mock_authenticate(self, conn):
            credentials = AuthCredentials(["authenticated"] + roles)
            return credentials, _AuthenticatedUser(mock_user)

        monkeypatch.setattr(JWTAuthMiddleware, "authenticate", mock_authenticate)
        return mock_user

    return _patch_user


class BaseAPITest:
    async def _create_user(self, async_client, username=None, email=None, password="gooD1@password"):
        username = username or f"user_{uuid.uuid4().hex[:6]}"
        email = email or f"{uuid.uuid4().hex[:6]}@gmail.com"
        payload = {
            "username": username,
            "email": email,
            "password": password,
            "password_repeat": password
        }
        response = await async_client.post("/auth/register", json=payload)
        assert response.status_code == 200
        return response.json()

    async def _create_role(self, async_client, auth_patch, name=None, perms=None):
        name = name or f"role_{uuid.uuid4().hex[:6]}"
        payload = {"name": name, "description": f"Test role {name}"}
        auth_patch(perms or ["perm:role:create"])
        response = await async_client.post("/role/create", json=payload)
        assert response.status_code == 200
        return response.json()

    async def _create_permission(self, async_client, auth_patch, name=None, perms=None):
        name = name or f"permission_{uuid.uuid4().hex[:6]}"
        payload = {
            "name": name,
            "resource": "test",
            "action": "test",
            "description": f"Test permission {name}"
        }
        auth_patch(perms or ["perm:permission:create"])
        response = await async_client.post("/permission/create", json=payload)
        assert response.status_code == 200
        return response.json()

    async def _assign_role_to_user(self, async_client, auth_patch, user_id, role_id, perms=None):
        auth_patch(perms or ["role:admin"])
        payload = {"user_id": user_id, "role_id": role_id}
        response = await async_client.post("/role/assign", json=payload)
        return response

    async def _assign_role_to_permission(self, async_client, auth_patch, permission_id, role_id, perms=None):
        auth_patch(perms or ["role:admin"])
        payload = {"permission_id": permission_id, "role_id": role_id}
        response = await async_client.post("/permission/assign", json=payload)
        return response