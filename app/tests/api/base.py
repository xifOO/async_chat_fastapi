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