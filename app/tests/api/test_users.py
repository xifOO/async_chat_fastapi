import pytest
from base import async_client


@pytest.mark.asyncio
class TestUsersApi:
    
    @pytest.mark.positive
    @pytest.mark.parametrize("payload", [
        ({"username": "test", "email": "test@gmail.com", "password": "gooD1@password"}),
    ])
    async def test_register_user_success(self, async_client, payload):
        response = await async_client.post("/auth/register", json=payload)
        assert response.status_code == 200
        assert response.json()["username"] == payload["username"]
        assert response.json()["email"] == payload["email"]
    

    @pytest.mark.validation
    @pytest.mark.parametrize("payload", [
        ({"username": "test", "email": "invalid", "password": "gooD@password"}), 
        ({"username": "", "email": "test@gmail.com", "password": "gooD@password"}),
        ({"username": "test", "email": "test@gmail.com", "password": "badpassword"}),    
    ])
    async def test_register_user_validation(self, async_client, payload):
        response = await async_client.post("/auth/register", json=payload)
        assert response.status_code == 422

    @pytest.mark.negative
    async def test_register_user_email_exists(self, async_client):
        first_user = {
            "username": "first_user", 
            "email": "exists@gmail.com", 
            "password": "gooD@password1"
        }
        response = await async_client.post("/auth/register", json=first_user)
        assert response.status_code == 200
    
        
        duplicate_user = {
            "username": "different_user", 
            "email": "exists@gmail.com", 
            "password": "gooD@password1"
        }
    
        response = await async_client.post("/auth/register", json=duplicate_user)
        assert response.status_code == 400
        assert "Email already exists" in response.json()["detail"]

    @pytest.mark.negative  
    async def test_register_user_name_exists(self, async_client):
        first_user = {
            "username": "exists_user", 
            "email": "first@gmail.com", 
            "password": "gooD@password1"
        }
        response = await async_client.post("/auth/register", json=first_user)
        assert response.status_code == 200
        
        duplicate_user = {
            "username": "exists_user", 
            "email": "second@gmail.com", 
            "password": "gooD@password1"
        }
        response = await async_client.post("/auth/register", json=duplicate_user)
        assert response.status_code == 400
        assert "Username already exists" in response.json()["detail"]