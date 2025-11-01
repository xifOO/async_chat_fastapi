from pydantic import ValidationError
import pytest

from app.models.models import Permission
from app.repositories.permission_repository import PermissionRepository

from app.schemas.permission import PermissionCreate, PermissionUpdate
from app.tests.conftest import test_session, test_db


@pytest.fixture
def repository():
    return PermissionRepository(Permission)


@pytest.mark.asyncio
class TestPermissionRepository:

    @pytest.mark.positive
    async def test_create(self, test_session, repository):
        permission_data = PermissionCreate(
            name="view_users",
            resource="user",
            action="read",
            description="can view users"
        )

        result = await repository.create(test_session, permission_data)

        assert result.name == "view_users"
        assert result.resource == "user"
        assert result.action == "read"
        assert result.description == "can view users"
        assert result in test_session

    @pytest.mark.validation
    @pytest.mark.parametrize("name,resource,action,description,expected_error", [
        ("", "user", "read", "desc", "Fields can't be empty"),
        ("   ", "user", "read", "desc", "Fields can't be empty"),
        ("\t", "user", "read", "desc", "Fields can't be empty"),
        ("view", "", "read", "desc", "Fields can't be empty"),
        ("view", "   ", "read", "desc", "Fields can't be empty"),
        ("view", "user", "", "desc", "Fields can't be empty"),
        ("view", "user", "   ", "desc", "Fields can't be empty"),
        (None, "user", "read", "desc", "Fields can't be empty"),
        ("view", None, "read", "desc", "Fields can't be empty"),
        ("view", "user", None, "desc", "Fields can't be empty"),
        ("view", "user", "read", None, "Fields can't be empty"),
        (None, None, None, None, "Fields can't be empty"),
    ])
    async def test_create_validation_errors(self, name, resource, action, description, expected_error):
        with pytest.raises(ValidationError) as exc_info:
            PermissionCreate(name=name, resource=resource, action=action, description=description)

        assert expected_error in str(exc_info.value)

    @pytest.mark.positive
    async def test_find_one_existing(self, test_db, repository):
        created_permission_id = None

        async with test_db.get_db_session() as create_session:
            permission_data = PermissionCreate(
                name="edit_users",
                resource="user",
                action="update",
                description="can edit users"
            )
            result = await repository.create(create_session, permission_data)
            await create_session.commit()
            created_permission_id = result.id

        async with test_db.get_db_session() as read_session:
            perm = await repository.find_one(read_session, id=created_permission_id)

            assert perm is not None
            assert perm.name == "edit_users"
            assert perm.resource == "user"
            assert perm.action == "update"
            assert perm.description == "can edit users"
            assert perm.id == created_permission_id

    @pytest.mark.positive
    async def test_find_one_non_existing(self, test_db, repository):
        async with test_db.get_db_session() as read_session:
            found = await repository.find_one(read_session, id=999)
            assert found is None

    @pytest.mark.positive
    async def test_update(self, test_db, repository):
        async with test_db.get_db_session() as create_session:
            permission_data = PermissionCreate(
                name="delete_users",
                resource="user",
                action="delete",
                description="delete users"
            )
            permission = await repository.create(create_session, permission_data)
            await create_session.commit()

        async with test_db.get_db_session() as update_session:
            update_data = PermissionUpdate(
                name="remove_users",
                resource="user",
                action="delete",
                description="remove users permanently"
            )
            updated = await repository.update(update_session, update_data, id=permission.id)
            await update_session.commit()

        assert updated.name == "remove_users"
        assert updated.description == "remove users permanently"
        assert updated.id == permission.id

    @pytest.mark.positive
    async def test_update_partial(self, test_db, repository):
        async with test_db.get_db_session() as create_session:
            permission_data = PermissionCreate(
                name="ban_users",
                resource="user",
                action="update",
                description="ban users"
            )
            permission = await repository.create(create_session, permission_data)
            await create_session.commit()

        async with test_db.get_db_session() as update_session:
            update_data = PermissionUpdate(
                description="ban and unban users"
            )
            updated = await repository.update(update_session, update_data, id=permission.id)
            await update_session.commit()

        assert updated.name == "ban_users" 
        assert updated.description == "ban and unban users"

    @pytest.mark.positive
    async def test_delete(self, test_db, repository):
        async with test_db.get_db_session() as create_session:
            permission_data = PermissionCreate(
                name="archive_users",
                resource="user",
                action="update",
                description="archive users"
            )
            permission = await repository.create(create_session, permission_data)
            await create_session.commit()

        async with test_db.get_db_session() as delete_session:
            await repository.delete(delete_session, id=permission.id)

        async with test_db.get_db_session() as read_session:
            found = await repository.find_one(read_session, id=permission.id)
            assert found is None

    @pytest.mark.positive
    @pytest.mark.parametrize("permissions_data", [
        [
            ("view_users", "user", "read", "view user list"),
            ("edit_users", "user", "update", "edit user info"),
            ("delete_users", "user", "delete", "remove user"),
        ]
    ])
    async def test_find_all(self, test_db, repository, permissions_data):
        async with test_db.get_db_session() as create_session:
            for name, resource, action, description in permissions_data:
                permission_data = PermissionCreate(
                    name=name,
                    resource=resource,
                    action=action,
                    description=description
                )
                await repository.create(create_session, permission_data)
            await create_session.commit()

        async with test_db.get_db_session() as read_session:
            all_permissions = await repository.find_all(read_session)

        assert len(all_permissions) == 3
        assert all(isinstance(perm, Permission) for perm in all_permissions)
