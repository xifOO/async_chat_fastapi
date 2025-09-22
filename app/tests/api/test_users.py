import logging
from unittest.mock import MagicMock, patch
import pytest
from app.schemas.user import UserSchema
from base import async_client, auth_patch


@pytest.mark.asyncio
class TestUsersApi:
    
    @pytest.mark.positive
    @pytest.mark.parametrize("payload", [
        ({"username": "test", "email": "test@gmail.com", "password": "gooD1@password", "password_repeat": "gooD1@password"}),
    ])
    async def test_register_user_success(self, async_client, payload):
        response = await async_client.post("/auth/register", json=payload)
        assert response.status_code == 200
        assert response.json()["username"] == payload["username"]
        assert response.json()["email"] == payload["email"]
        assert "password" not in response.json()
    
    @pytest.mark.validation
    @pytest.mark.parametrize("payload", [
        ({"username": "test", "email": "invalid", "password": "gooD@password", "password_repeat": "gooD@password"}), 
        ({"username": "", "email": "test@gmail.com", "password": "gooD@password1", "password_repeat": "gooD@password1"}),
        ({"username": "test", "email": "test@gmail.com", "password": "badpassword", "password_repeat": "badpassword"}),
        ({"username": "test", "email": "test@gmail.com", "password": " ", "password_repeat": " "}),    
        ({"username": "test", "email": "test@gmail.com", "password": "password", "password_repeat": "notpassword"}),      
    ])
    async def test_register_user_validation(self, async_client, payload):
        response = await async_client.post("/auth/register", json=payload)
        assert response.status_code == 422

    @pytest.mark.negative
    async def test_register_user_email_exists(self, async_client):
        first_user = {
            "username": "first_user", 
            "email": "exists@gmail.com", 
            "password": "gooD@password1",
            "password_repeat": "gooD@password1"
        }
        response = await async_client.post("/auth/register", json=first_user)
        assert response.status_code == 200
    
        duplicate_user = {
            "username": "different_user", 
            "email": "exists@gmail.com", 
            "password": "gooD@password1",
            "password_repeat": "gooD@password1"
        }
    
        response = await async_client.post("/auth/register", json=duplicate_user)
        assert response.status_code == 400
        assert "Email already exists" in response.json()["detail"]

    @pytest.mark.negative  
    async def test_register_user_name_exists(self, async_client):
        first_user = {
            "username": "exists_user", 
            "email": "first@gmail.com", 
            "password": "gooD@password1",
            "password_repeat": "gooD@password1"
        }
        response = await async_client.post("/auth/register", json=first_user)
        assert response.status_code == 200
        
        duplicate_user = {
            "username": "exists_user", 
            "email": "second@gmail.com", 
            "password": "gooD@password1",
            "password_repeat": "gooD@password1"
        }
        response = await async_client.post("/auth/register", json=duplicate_user)
        assert response.status_code == 400
        assert "Username already exists" in response.json()["detail"]

    @pytest.mark.positive
    async def test_login_success(self, async_client):
        register_data = {
            "username": "login", 
            "email": "login@gmail.com", 
            "password": "gooD@password1",
            "password_repeat": "gooD@password1"
        }
        await async_client.post("/auth/register", json=register_data)

        login_data = {
            "username": "login",
            "password": "gooD@password1"
        }
        response = await async_client.post("/auth/login", data=login_data)
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"

    @pytest.mark.negative
    async def test_login_invalid_user(self, async_client):
        login_data = {
            "username": "invalid",
            "password": "invalid"
        }
        response = await async_client.post("/auth/login", data=login_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    @pytest.mark.negative
    @pytest.mark.parametrize("login_data", [
        ({"username": "login", "password": "incorrect"}), 
        ({"username": "incorrect", "password": "gooD@password1"}),  
    ])
    async def test_login_fields_incorrect(self, async_client, login_data):
        register_data = {
            "username": "login", 
            "email": "login@gmail.com", 
            "password": "gooD@password1",
            "password_repeat": "gooD@password1"
        }
        await async_client.post("/auth/register", json=register_data)

        response = await async_client.post("/auth/login", data=login_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    @pytest.mark.positive
    async def test_refresh_cookies_success(self, async_client):
        register_data = {
            "username": "login", 
            "email": "login@gmail.com", 
            "password": "gooD@password1",
            "password_repeat": "gooD@password1"
        }
        await async_client.post("/auth/register", json=register_data)

        login_data = {
            "username": "login",
            "password": "gooD@password1"
        }
        response = await async_client.post("/auth/login", data=login_data)
        assert "refresh_token" in response.cookies
        assert len(response.cookies.get("refresh_token")) > 0
    
    @pytest.mark.positive
    async def test_delete_user_as_admin_success(self, async_client, auth_patch):
        register_data = {
            "username": "to_delete",
            "email": "delete@gmail.com",
            "password": "gooD@password1",
            "password_repeat": "gooD@password1"
        }
        user_response = await async_client.post("/auth/register", json=register_data)
        user_id = user_response.json()["id"]
        auth_patch(["role:admin"])
        response = await async_client.delete(f"/auth/delete/{user_id}", headers={"Authorization": "Bearer test"})
        assert response.status_code == 204
    
    @pytest.mark.negative
    async def test_delete_forbidden_user(self, async_client, auth_patch):
        register_data = {
            "username": "to_delete",
            "email": "delete@gmail.com",
            "password": "gooD@password1",
            "password_repeat": "gooD@password1"
        }
        user_response = await async_client.post("/auth/register", json=register_data)
        user_id = user_response.json()["id"]
        auth_patch(["role:nonadmin"])
        response = await async_client.delete(f"/auth/delete/{user_id}", headers={"Authorization": "Bearer test"})
        assert response.status_code == 403
    
    @pytest.mark.validation
    @pytest.mark.parametrize("user_id", [
        ([1]),  
        (["1"]), 
        (),  
        ("invalid"),
    ])
    async def test_delete_user_validation(self, async_client, auth_patch, user_id):
        auth_patch(["role:admin"])
        response = await async_client.delete(f"/auth/delete/{user_id}", headers={"Authorization": "Bearer test"})
        assert response.status_code == 422
    
    