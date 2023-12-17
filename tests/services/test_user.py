import pytest
from db.models import User

from schemas.user import UserCreate, UserState
from pydantic import SecretStr
from sqlmodel import Session
from fastapi import HTTPException, status
from services.user import user
from tests.test_main import session_fixture
from auth.auth import public_key, create_access_token, private_key
import datetime


class TestGetUserByUsername:
    user_create = UserCreate(username="testuser", email="testuser@example.com", password=SecretStr("Test_1234!"))
    
    def test_get_user(self, session: Session):
        # Test Case 1: To get user in db
        user_obj = user.create(session, self.user_create)
        user_dict = user.get_username(session, user_obj.username)
        
        if user_dict is None:
            pytest.fail("User not found")
        
        assert user_dict.username == "testuser"
        assert user_dict.email == "testuser@example.com"
    
    def test_bad_user(self, session: Session):
        user.create(session, self.user_create)
        
        with pytest.raises(HTTPException) as exc_info:
            user.get_username(session, "testuser1")
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "User not found"

class TestCreateUser:
    def test_create_new_user(self, session: Session):
        # Test Case 1: Create a new user
        user_create = UserCreate(username="testuser", email="testuser@example.com", password=SecretStr("Test_1234!"))
        user_obj = user.create(session, user_create)
        assert user_obj.username == "testuser"
        assert user_obj.password_hash != "Test_1234!"
        assert isinstance(user_obj.created_at, datetime.datetime)
        
    def test_existing_username(self, session: Session):
        # Test case 2: Try to create a user with an existing username and email
        user_create1 = UserCreate(username="testuser1", email="testuser1@example.com", password=SecretStr("Test_1234!"))
        user.create(session, user_create1)

        with pytest.raises(HTTPException) as exc_info:
            user_create2 = UserCreate(username="testuser1", email="testuser2@example.com", password=SecretStr("Test_5678!"))
            user.create(session, user_create2)
    
        assert exc_info.value.status_code == status.HTTP_409_CONFLICT
        assert "User already exists" in str(exc_info.value.detail)

@pytest.fixture
def add_user_in_db(session: Session) -> User:
    username = "testuser"
    email = "testuser@example.com"
    password = SecretStr("Test_1234!")
    obj_in = UserCreate(username=username, email=email, password=password)
    user_db = user.create(session, obj_in)
    
    payload = UserState(username=username, email=email, is_vendor=False, exp=datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15), is_superuser=False)
    token = create_access_token(payload, private_key)
    user_db.auth_token = token
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    
    return user_db
    
# class TestGetCurrentUser:
#     def test_get_current_user(self, session: Session, create_test_user: tuple[str, str, SecretStr]):
#         username, email, password = create_test_user
        
#         payload = UserState(username=username, email=email, is_vendor=False, exp=datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15), is_superuser=False)
        
#         token = create_access_token(payload, private_key)
#         user_data = user.get_username(session, username)
        
        
#         user_obj = user.get_current_user(public_key, token, session)
        
#         if user_obj is None:
#             pytest.fail("User not found")
        
#         assert user_obj.username == username
#         assert user_obj.email == email
#         assert isinstance(user_obj.last_signed_in, datetime.datetime)
#         assert user_obj.id is not None
        
#     def test_bad_username(self, session: Session, create_test_user: tuple[str, str, SecretStr]):
#         username, email, password = create_test_user
        
#         payload = UserState(username="test", email=email, is_vendor=False, is_superuser=False, exp=datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15))
        
#         token = create_access_token(payload, private_key)
        
#         with pytest.raises(HTTPException) as exc_info:
#             user.get_current_user(public_key, token, session)
        
#         assert exc_info.value.status_code == 404
#         assert exc_info.value.detail == "User not found"
