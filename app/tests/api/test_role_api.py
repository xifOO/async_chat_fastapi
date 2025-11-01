import pytest
from base import BaseAPITest, async_client, auth_patch


@pytest.mark.asyncio
class TestRoleAPI(BaseAPITest):

    @pytest.mark.positive
    async def test_create_role_success(self, async_client, auth_patch):
        role = await self._create_role(async_client, auth_patch, name="test")
        assert role["name"] == "test"
        assert role["description"] == "Test role test"
        

    @pytest.mark.validation
    @pytest.mark.parametrize("payload", [
        {"name": "", "description": "test"},
        {"name": "", "description": ""},
        {"name": "test", "description": ""},
    ])
    async def test_create_role_validation(self, async_client, auth_patch, payload):
        auth_patch(["perm:role:create"])
        response = await async_client.post("/roles/", json=payload)
        assert response.status_code == 422

    @pytest.mark.negative
    async def test_create_role_forbidden(self, async_client, auth_patch):
        auth_patch(["perm:role:delete"])
        payload = {"name": "test", "description": "test"}
        response = await async_client.post("/roles/", json=payload)
        assert response.status_code == 403

    @pytest.mark.negative
    async def test_create_role_exists(self, async_client, auth_patch):
        await self._create_role(async_client, auth_patch, name="test")
        response = await async_client.post(
            "/roles/",
            json={"name": "test", "description": "test"},
        )
        assert response.status_code == 400
        assert "Record already exists" in response.json()["detail"]

    @pytest.mark.positive
    async def test_assign_role_to_user_success(self, async_client, auth_patch):
        user = await self._create_user(async_client)
        role = await self._create_role(async_client, auth_patch)
        response = await self._assign_role_to_user(
            async_client, auth_patch, user["id"], role["id"]
        )
        assert response.status_code in (200, 204)

    @pytest.mark.negative
    async def test_assign_role_to_invalid_user(self, async_client, auth_patch):
        role = await self._create_role(async_client, auth_patch)
        response = await self._assign_role_to_user(
            async_client, auth_patch, user_id=99999, role_id=role["id"]
        )
        assert response.status_code == 404

    @pytest.mark.negative
    async def test_assign_invalid_role(self, async_client, auth_patch):
        user = await self._create_user(async_client)
        response = await self._assign_role_to_user(
            async_client, auth_patch, user["id"], role_id=99999
        )
        assert response.status_code == 404

    @pytest.mark.negative
    async def test_forbidden_assign_role_to_user(self, async_client, auth_patch):
        user = await self._create_user(async_client)
        role = await self._create_role(async_client, auth_patch)
        response = await self._assign_role_to_user(
            async_client, auth_patch, user["id"], role["id"], perms=["role:nonadmin"]
        )
        assert response.status_code == 403
