from httpx import ASGITransport, AsyncClient
import pytest_asyncio


@pytest_asyncio.fixture
async def async_client(test_db, monkeypatch):
    from app.main import app
    from app.db.db import db 
    
    monkeypatch.setattr(db, "get_db_session", test_db.get_db_session)
    
    async with AsyncClient(transport=ASGITransport(app=app), 
                         base_url="http://test") as client:
        yield client