from pydantic import ValidationError
import pytest

from app.models.models import Role
from app.repositories.role_repository import RoleRepository

from app.schemas.role import RoleCreate, RoleUpdate
from app.tests.conftest import test_session, test_db


@pytest.fixture
def repository():
    return RoleRepository(Role)


@pytest.mark.asyncio
class TestRoleRepository:

    @pytest.mark.positive
    async def test_create(self, test_session, repository):
        role_data = RoleCreate(name="admin", description="role for admin")

        result = await repository.create(test_session, role_data)
        
        assert result.name == "admin"
        assert result.description == "role for admin"

        assert result in test_session
    
    @pytest.mark.validation
    @pytest.mark.parametrize("name,description,expected_error", [
        ("", "valid description", "Fields can't be empty"),
        (" ", "valid description", "Fields can't be empty"),
        ("\t", "valid description", "Fields can't be empty"),
        ("valid name", "", "Fields can't be empty"),
        ("valid name", " ", "Fields can't be empty"),
        ("valid name", "\t", "Fields can't be empty"),
        ("", "", "Fields can't be empty"),
        (" ", " ", "Fields can't be empty"),
        (None, "valid description", "Fields can't be empty"), 
        ("valid name", None, "Fields can't be empty"),         
        (None, None, "Fields can't be empty"),                 
    ])
    async def test_create_validation_errors(self, name, description, expected_error):
        with pytest.raises(ValidationError) as exc_info:
            RoleCreate(name=name, description=description)

        assert expected_error in str(exc_info.value)
    
    @pytest.mark.positive
    async def test_find_one_existing(self, test_db, repository):
        created_role_id = None
        
        async with test_db.get_db_session() as create_session:
            role_data = RoleCreate(name="admin", description="role for admin")
            result = await repository.create(create_session, role_data)
            await create_session.commit()
            created_role_id = result.id
        

        async with test_db.get_db_session() as read_session:
            role = await repository.find_one(read_session, id=created_role_id)
            
            assert role is not None
            assert role.name == "admin"
            assert role.description == "role for admin"
            assert role.id == created_role_id
    
    @pytest.mark.positive
    async def test_find_one_non_existing(self, test_db, repository):
        async with test_db.get_db_session() as read_session:
            found = await repository.find_one(read_session, id=999)
            assert found is None
    
    @pytest.mark.positive
    async def test_update(self, test_db, repository):
        async with test_db.get_db_session() as create_session:
            role_data = RoleCreate(name="old_name", description="old_description")
            role = await repository.create(create_session, role_data)
            await create_session.commit()
        
        async with test_db.get_db_session() as update_session:
            update_data = RoleUpdate(name="new_name", description="new_description")
            updated = await repository.update(update_session, update_data, id=role.id)
            await update_session.commit()
        
        assert updated.name == "new_name"
        assert updated.description == "new_description"
        assert updated.id == role.id
    
    @pytest.mark.positive
    async def test_update_partial(self, test_db, repository):
        async with test_db.get_db_session() as create_session:
            role_data = RoleCreate(name="old_name", description="old_description")
            role = await repository.create(create_session, role_data)
            await create_session.commit()
        
        async with test_db.get_db_session() as update_session:
            update_data = RoleUpdate(name="new_name")
            updated = await repository.update(update_session, update_data, id=role.id)
            await update_session.commit()
        
        assert updated.name == "new_name"
        assert updated.description == "old_description"
    
    @pytest.mark.positive
    async def test_delete(self, test_db, repository):
        async with test_db.get_db_session() as create_session:
            role_data = RoleCreate(name="to_delete", description="to delete description")
            role = await repository.create(create_session, role_data)
            await create_session.commit()

        async with test_db.get_db_session() as delete_session:
            await repository.delete(delete_session, id=role.id)
        
        async with test_db.get_db_session() as read_session:
            found = await repository.find_one(read_session, id=role.id)
            assert found is None
    
    @pytest.mark.positive
    @pytest.mark.parametrize("roles_data" ,[
        [
            ("admin", "admin role"),
            ("user", "user role"), 
            ("moderator", "moderator role")
        ]
    ])
    async def test_find_all(self, test_db, repository, roles_data):
        async with test_db.get_db_session() as create_session:
            for name, description in roles_data:
                role_data = RoleCreate(name=name, description=description)
                role = await repository.create(create_session, role_data)
            await create_session.commit()

        async with test_db.get_db_session() as read_session:
            all_roles = await repository.find_all(read_session)
        
        assert len(all_roles) == 3
        assert all(isinstance(role, Role) for role in all_roles)
    
    @pytest.mark.positive
    async def test_find_multiple_with_permissions_existing_roles(self, test_db, repository):
        async with test_db.get_db_session() as create_session:
            admin_role = RoleCreate(name="admin", description="admin role")
            user_role = RoleCreate(name="user", description="user role")
            moderator_role = RoleCreate(name="moderator", description="moderator role")
            
            await repository.create(create_session, admin_role)
            await repository.create(create_session, user_role)
            await repository.create(create_session, moderator_role)
            await create_session.commit()

        async with test_db.get_db_session() as read_session:
            role_names = ["admin", "user"]
            roles = await repository.find_multiple_with_permissions(read_session, role_names)
            
            assert len(roles) == 2
            assert all(isinstance(role, Role) for role in roles)
            
            role_names_found = [role.name for role in roles]
            assert "admin" in role_names_found
            assert "user" in role_names_found
            assert "moderator" not in role_names_found

            for role in roles:
                assert hasattr(role, 'permissions')
    
    @pytest.mark.positive
    async def test_find_multiple_with_permissions_partial_existing(self, test_db, repository):
        async with test_db.get_db_session() as create_session:
            admin_role = RoleCreate(name="admin", description="admin role")
            await repository.create(create_session, admin_role)
            await create_session.commit()

        async with test_db.get_db_session() as read_session:
            role_names = ["admin", "nonexistent"]
            roles = await repository.find_multiple_with_permissions(read_session, role_names)
            
            assert len(roles) == 1
            assert roles[0].name == "admin"
            assert hasattr(roles[0], 'permissions')