from pydantic import ValidationError
import pytest

from app.models.models import User
from app.repositories.users_repository import UserRepository

from app.schemas.user import UserCreate, UserInDB, UserUpdate
from app.security import get_password_hash
from app.tests.conftest import test_session, test_db


@pytest.fixture
def repository():
    return UserRepository(User)

@pytest.mark.asyncio
class TestUserRepository:

    @pytest.mark.positive
    async def test_create(self, test_session, repository):
        user_data = UserCreate(username="user", email="user@gmail.com", password="gooD@password1", password_repeat="gooD@password1")
        db_user = UserInDB(
            username=user_data.username,
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
        )
        result = await repository.create(test_session, db_user)
        
        assert result.username == "user"
        assert result.email == "user@gmail.com"

        assert result in test_session

    @pytest.mark.validation
    @pytest.mark.parametrize("username,email,password,password_repeat,expected_error", [
        ("", "user@gmail.com", "gooD@password1", "gooD@password1", "Username can't be empty"),
        ("   ", "user@gmail.com", "gooD@password1", "gooD@password1", "Username can't be empty"),
        ("\t", "user@gmail.com", "gooD@password1", "gooD@password1", "Username can't be empty"),
        ("usr", "user@gmail.com", "gooD@password1", "gooD@password1", "Username must be at least 4 characters long"),
        ("user", "invalid-email", "gooD@password1", "gooD@password1", "value is not a valid email address"),
        ("user", "user@gmail.com", "weak", "weak", "You have entered an invalid password"),
        ("user", "user@gmail.com", "gooD@password1", "different", "Passwords do not match"),
        (None, "user@gmail.com", "gooD@password1", "gooD@password1", "Username can't be empty"),
        ("user", "invalid-email", "gooD@password1", "gooD@password1", "value is not a valid email address"),
        ("user", "user@gmail.com", "NoDigit!", "NoDigit!", "You have entered an invalid password"),
        ("user", "user@gmail.com", "nouppercase1!", "nouppercase1!", "You have entered an invalid password"),
        ("user", "user@gmail.com", "NOLOWERCASE1!", "NOLOWERCASE1!", "You have entered an invalid password"),
        ("user", "user@gmail.com", "NoSpecial1", "NoSpecial1", "You have entered an invalid password"),
        ("user", "user@gmail.com", "Sh1!", "Sh1!", "You have entered an invalid password"),
    ])
    async def test_create_validation_errors(self, username, email, password, password_repeat, expected_error):
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(username=username, email=email, password=password, password_repeat=password_repeat)
        
        assert expected_error in str(exc_info.value)
    
    @pytest.mark.positive
    async def test_find_one_existing(self, test_db, repository):
        created_user_id = None
        
        async with test_db.get_db_session() as create_session:
            db_user = UserInDB(
                username="testuser",
                email="test@example.com",
                hashed_password=get_password_hash("password123A!")
            )
            result = await repository.create(create_session, db_user)
            await create_session.commit()
            created_user_id = result.id

        async with test_db.get_db_session() as read_session:
            user = await repository.find_one(read_session, id=created_user_id)
            
            assert user is not None
            assert user.username == "testuser"
            assert user.email == "test@example.com"
            assert user.id == created_user_id

    @pytest.mark.positive
    async def test_find_one_non_existing(self, test_db, repository):
        async with test_db.get_db_session() as read_session:
            found = await repository.find_one(read_session, id=999)
            assert found is None

    @pytest.mark.positive
    async def test_find_one_by_email(self, test_db, repository):
        async with test_db.get_db_session() as create_session:
            db_user = UserInDB(
                username="emailtest",
                email="email@test.com",
                hashed_password=get_password_hash("password123A!")
            )
            await repository.create(create_session, db_user)
            await create_session.commit()

        async with test_db.get_db_session() as read_session:
            user = await repository.find_one(read_session, email="email@test.com")
            
            assert user is not None
            assert user.email == "email@test.com"
            assert user.username == "emailtest"

    @pytest.mark.positive
    async def test_find_one_by_username(self, test_db, repository):
        async with test_db.get_db_session() as create_session:
            db_user = UserInDB(
                username="usernametest",
                email="username@test.com",
                hashed_password=get_password_hash("password123A!")
            )
            await repository.create(create_session, db_user)
            await create_session.commit()

        async with test_db.get_db_session() as read_session:
            user = await repository.find_one(read_session, username="usernametest")
            
            assert user is not None
            assert user.username == "usernametest"
            assert user.email == "username@test.com"

    @pytest.mark.positive
    async def test_update(self, test_db, repository):
        async with test_db.get_db_session() as create_session:
            db_user = UserInDB(
                username="olduser",
                email="old@example.com",
                hashed_password=get_password_hash("password123A!")
            )
            user = await repository.create(create_session, db_user)
            await create_session.commit()

        async with test_db.get_db_session() as update_session:
            update_data = UserUpdate(username="newuser", email="new@example.com")
            updated = await repository.update(update_session, update_data, id=user.id)
            await update_session.commit()

        assert updated.username == "newuser"
        assert updated.email == "new@example.com"
        assert updated.id == user.id

    @pytest.mark.positive
    async def test_update_partial(self, test_db, repository):
        async with test_db.get_db_session() as create_session:
            db_user = UserInDB(
                username="partialuser",
                email="partial@example.com",
                hashed_password=get_password_hash("password123A!")
            )
            user = await repository.create(create_session, db_user)
            await create_session.commit()

        async with test_db.get_db_session() as update_session:
            update_data = UserUpdate(username="updateduser")
            updated = await repository.update(update_session, update_data, id=user.id)
            await update_session.commit()

        assert updated.username == "updateduser"
        assert updated.email == "partial@example.com"

    @pytest.mark.positive
    async def test_delete(self, test_db, repository):
        async with test_db.get_db_session() as create_session:
            db_user = UserInDB(
                username="deleteuser",
                email="delete@example.com",
                hashed_password=get_password_hash("password123A!")
            )
            user = await repository.create(create_session, db_user)
            await create_session.commit()

        async with test_db.get_db_session() as delete_session:
            await repository.delete(delete_session, id=user.id)
            await delete_session.commit()

        async with test_db.get_db_session() as read_session:
            found = await repository.find_one(read_session, id=user.id)
            assert found is None

    @pytest.mark.positive
    @pytest.mark.parametrize("users_data", [
        [
            ("admin", "admin@example.com"),
            ("user1", "user1@example.com"),
            ("moderator", "mod@example.com")
        ]
    ])
    async def test_find_all(self, test_db, repository, users_data):
        async with test_db.get_db_session() as create_session:
            for username, email in users_data:
                db_user = UserInDB(
                    username=username,
                    email=email,
                    hashed_password=get_password_hash("password123A!")
                )
                await repository.create(create_session, db_user)
            await create_session.commit()

        async with test_db.get_db_session() as read_session:
            all_users = await repository.find_all(read_session)

        assert len(all_users) == 3
        assert all(isinstance(user, User) for user in all_users)

    @pytest.mark.positive
    async def test_exists_true(self, test_db, repository):
        async with test_db.get_db_session() as create_session:
            db_user = UserInDB(
                username="existsuser",
                email="exists@example.com",
                hashed_password=get_password_hash("password123A!")
            )
            await repository.create(create_session, db_user)
            await create_session.commit()

        async with test_db.get_db_session() as read_session:
            exists = await repository.exists(read_session, email="exists@example.com")
            assert exists is True

    @pytest.mark.positive
    async def test_exists_false(self, test_db, repository):
        async with test_db.get_db_session() as read_session:
            exists = await repository.exists(read_session, email="nonexistent@example.com")
            assert exists is False

    @pytest.mark.positive
    async def test_exists_by_username(self, test_db, repository):
        async with test_db.get_db_session() as create_session:
            db_user = UserInDB(
                username="uniqueuser",
                email="unique@example.com",
                hashed_password=get_password_hash("password123A!")
            )
            await repository.create(create_session, db_user)
            await create_session.commit()

        async with test_db.get_db_session() as read_session:
            exists = await repository.exists(read_session, username="uniqueuser")
            assert exists is True

    @pytest.mark.positive
    async def test_find_with_roles(self, test_db, repository):
        async with test_db.get_db_session() as create_session:
            db_user = UserInDB(
                username="roleuser",
                email="roles@example.com",
                hashed_password=get_password_hash("password123A!")
            )
            user = await repository.create(create_session, db_user)
            await create_session.commit()

        async with test_db.get_db_session() as read_session:
            user_with_roles = await repository.find_with_roles(read_session, id=user.id)
            
            assert user_with_roles is not None
            assert user_with_roles.username == "roleuser"
            assert hasattr(user_with_roles, 'roles')

    @pytest.mark.positive
    async def test_find_with_roles_non_existing(self, test_db, repository):
        async with test_db.get_db_session() as read_session:
            user_with_roles = await repository.find_with_roles(read_session, id=999)
            assert user_with_roles is None

    @pytest.mark.positive
    async def test_find_all_with_pagination(self, test_db, repository):
        async with test_db.get_db_session() as create_session:
            for i in range(5):
                db_user = UserInDB(
                    username=f"user{i}",
                    email=f"user{i}@example.com",
                    hashed_password=get_password_hash("password123A!")
                )
                await repository.create(create_session, db_user)
            await create_session.commit()

        async with test_db.get_db_session() as read_session:
            users_limited = await repository.find_all(read_session, limit=3)
            assert len(users_limited) == 3

            users_offset = await repository.find_all(read_session, limit=2, offset=2)
            assert len(users_offset) == 2
    
    @pytest.mark.positive
    async def test_multiple_filters(self, test_db, repository):
        async with test_db.get_db_session() as create_session:
            db_user = UserInDB(
                username="multifilter",
                email="multi@filter.com",
                hashed_password=get_password_hash("password123A!")
            )
            user = await repository.create(create_session, db_user)
            await create_session.commit()

        async with test_db.get_db_session() as read_session:
            found_user = await repository.find_one(
                read_session, 
                username="multifilter", 
                email="multi@filter.com"
            )
            
            assert found_user is not None
            assert found_user.id == user.id
            assert found_user.username == "multifilter"
            assert found_user.email == "multi@filter.com"