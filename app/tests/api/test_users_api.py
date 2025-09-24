import uuid
import pytest
from app.schemas.user import UserUpdate
from base import BaseAPITest, async_client, auth_patch


@pytest.mark.asyncio
class TestUsersAPI(BaseAPITest):

    async def _register_user(self, async_client, username=None, email=None, password="gooD@password1"):
        username = username or f"user_{uuid.uuid4().hex[:6]}"
        email = email or f"{uuid.uuid4().hex[:6]}@gmail.com"
        payload = {
            "username": username,
            "email": email,
            "password": password,
            "password_repeat": password
        }
        response = await async_client.post("/auth/register", json=payload)
        return response

    async def _login_user(self, async_client, username, password="gooD@password1"):
        login_data = {"username": username, "password": password}
        response = await async_client.post("/auth/login", data=login_data)
        return response

    @pytest.mark.positive
    async def test_register_user_success(self, async_client):
        response = await self._register_user(async_client, username="test", email="test@gmail.com")
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "test"
        assert data["email"] == "test@gmail.com"
        assert "password" not in data

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
        first = await self._register_user(async_client, username="first_user", email="exists@gmail.com")
        assert first.status_code == 200

        duplicate = await self._register_user(async_client, username="different_user", email="exists@gmail.com")
        assert duplicate.status_code == 400
        assert "Email already exists" in duplicate.json()["detail"]

    @pytest.mark.negative  
    async def test_register_user_name_exists(self, async_client):
        first = await self._register_user(async_client, username="exists_user", email="first@gmail.com")
        assert first.status_code == 200

        duplicate = await self._register_user(async_client, username="exists_user", email="second@gmail.com")
        assert duplicate.status_code == 400
        assert "Username already exists" in duplicate.json()["detail"]

    @pytest.mark.positive
    async def test_login_success(self, async_client):
        await self._register_user(async_client, username="login", email="login@gmail.com")
        response = await self._login_user(async_client, username="login")
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.negative
    async def test_login_invalid_user(self, async_client):
        response = await self._login_user(async_client, username="invalid", password="invalid")
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    @pytest.mark.negative
    @pytest.mark.parametrize("login_data", [
        ({"username": "login", "password": "incorrect"}), 
        ({"username": "incorrect", "password": "gooD@password1"}),  
    ])
    async def test_login_fields_incorrect(self, async_client, login_data):
        await self._register_user(async_client, username="login", email="login@gmail.com")
        response = await async_client.post("/auth/login", data=login_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    @pytest.mark.positive
    async def test_refresh_cookies_success(self, async_client):
        await self._register_user(async_client, username="login", email="login@gmail.com")
        response = await self._login_user(async_client, username="login")
        assert "refresh_token" in response.cookies
        assert len(response.cookies.get("refresh_token")) > 0

    @pytest.mark.positive
    async def test_delete_user_as_admin_success(self, async_client, auth_patch):
        user_response = await self._register_user(async_client, username="to_delete", email="delete@gmail.com")
        user_id = user_response.json()["id"]
        auth_patch(["role:admin"])
        response = await async_client.delete(f"/auth/delete/{user_id}", headers={"Authorization": "Bearer test"})
        assert response.status_code == 204

    @pytest.mark.negative
    async def test_delete_forbidden_user(self, async_client, auth_patch):
        user_response = await self._register_user(async_client, username="to_delete", email="delete@gmail.com")
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
    
    @pytest.mark.positive
    async def test_update_user_success(self, async_client, auth_patch):
        user_response = await self._register_user(async_client, username="to_update", email="to_update@gmail.com")
        user_id = user_response.json()["id"]

        mock_user = auth_patch(["perm:no_permission"])
        mock_user.id = user_id # request.id == user_id

        update_data = UserUpdate(username="update", email="update@gmail.com")
        response = await async_client.patch(
            f"/auth/update/{user_id}",
            headers={"Authorization": "Bearer test"},
            json=update_data.model_dump()
        )

        assert response.status_code == 200

        data = response.json()
        assert data["username"] == update_data.username
        assert data["email"] == update_data.email
    
    @pytest.mark.negative
    async def test_update_forbidden_user(self, async_client, auth_patch):
        user_response = await self._register_user(async_client, username="to_update", email="to_update@gmail.com")
        user_id = user_response.json()["id"]

        auth_patch(["perm:user:nonupdate"])

        update_data = UserUpdate(username="update", email="update@gmail.com")
        response = await async_client.patch(
            f"/auth/update/{user_id}",
            headers={"Authorization": "Bearer test"},
            json=update_data.model_dump()
        )

        assert response.status_code == 403
    
    @pytest.mark.validation
    @pytest.mark.parametrize("user_id", [
        [1],       
        ["1"],    
        (),        
        "invalid"  
    ])
    async def test_update_user_validation(self, async_client, auth_patch, user_id):
        auth_patch(["perm:update:user"])
        update_data = UserUpdate(username="update", email="update@gmail.com")

        response = await async_client.patch(
            f"/auth/update/{user_id}",
            headers={"Authorization": "Bearer test"},
            json=update_data.model_dump()
        )

        assert response.status_code == 422
    
    @pytest.mark.validation
    @pytest.mark.parametrize("username, email, expected_error", [
        ("", "valid@example.com", "Username can't be empty"),
        ("   ", "valid@example.com", "Username can't be empty"),
        ("abc", "valid@example.com", "Username must be at least 4 characters long"),
        ("validname", "invalidemail", "value is not a valid email address"),
    ])
    async def test_update_user_invalid_data(self, async_client, auth_patch, username, email, expected_error):
        user_response = await self._register_user(async_client, username="update", email="update@gmail.com")
        user_id = user_response.json()["id"]

        auth_patch(["perm:update:user"])
        update_data = {"username": username, "email": email}

        response = await async_client.patch(
            f"/auth/update/{user_id}",
            headers={"Authorization": "Bearer test"},
            json=update_data
        )

        assert response.status_code == 422
        assert expected_error in response.text