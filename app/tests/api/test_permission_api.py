import pytest
from base import BaseAPITest, async_client, auth_patch


@pytest.mark.asyncio
class TestPermissionAPI(BaseAPITest):

    @pytest.mark.positive
    async def test_create_permission_success(self, async_client, auth_patch):
        perm = await self._create_permission(async_client, auth_patch, name="test")
        assert perm["name"] == "test"
        assert perm["resource"] == "test"
        assert perm["action"] == "test"

    @pytest.mark.validation
    @pytest.mark.parametrize("payload", [
        ({"name": "test", "resource": "test", "action": "", "description": "test"}), 
        ({"name": "", "resource": "test", "action": "test", "description": "test"}),
        ({"name": "test", "resource": "", "action": "test", "description": ""}),     
    ])
    async def test_create_permission_validation(self, async_client, auth_patch, payload):
        auth_patch(["perm:permission:create"])
        response = await async_client.post("/permission/create", json=payload)
        assert response.status_code == 422

    @pytest.mark.negative
    async def test_create_permission_forbidden(self, async_client, auth_patch):
        auth_patch(["perm:permission:delete"])
        payload = {
            "name": "test",
            "resource": "test",
            "action": "test",
            "description": "test"
        }
        response = await async_client.post("/permission/create", json=payload)
        assert response.status_code == 403

    @pytest.mark.negative
    async def test_create_permission_exists(self, async_client, auth_patch):
        await self._create_permission(async_client, auth_patch, name="test")
        response = await async_client.post("/permission/create", json={
            "name": "test", "resource": "test", "action": "test", "description": "test"
        })
        assert response.status_code == 400
        assert "Record already exists" in response.json()["detail"]

    @pytest.mark.positive
    async def test_assign_role_to_permission_success(self, async_client, auth_patch):
        permission = await self._create_permission(async_client, auth_patch)
        role = await self._create_role(async_client, auth_patch)
        response = await self._assign_role_to_permission(async_client, auth_patch, permission["id"], role["id"])
        assert response.status_code == 200

    @pytest.mark.negative
    async def test_assign_role_to_invalid_user(self, async_client, auth_patch):
        role = await self._create_role(async_client, auth_patch)
        response = await self._assign_role_to_permission(async_client, auth_patch, 99999, role["id"])
        assert response.status_code == 400

    @pytest.mark.negative
    async def test_assign_invalid_role(self, async_client, auth_patch):
        permission = await self._create_permission(async_client, auth_patch)
        response = await self._assign_role_to_permission(async_client, auth_patch, permission["id"], 99999)
        assert response.status_code == 400

    @pytest.mark.negative
    async def test_forbidden_assign_role_to_user(self, async_client, auth_patch):
        permission = await self._create_permission(async_client, auth_patch)
        role = await self._create_role(async_client, auth_patch)
        response = await self._assign_role_to_permission(async_client, auth_patch, permission["id"], role["id"], perms=["role:nonadmin"])
        assert response.status_code == 403