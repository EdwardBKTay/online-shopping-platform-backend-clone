import pytest

from fastapi import HTTPException, status
from sqlmodel import Session
from schemas.user import UserCreate
from crud.crud_user import user
from tests.test_main import session_fixture
from pydantic import SecretStr
import datetime

class TestGetUserByUsername:
    user_create = UserCreate(username="testuser", email="testuser@example.com", password=SecretStr("Test_1234!"))
    
    def test_get_user(self, session: Session):
        # Test Case 1: To get user in db
        user_obj = user.create(session, self.user_create)
        user_dict = user.get(session, user_obj.username)
        
        assert user_dict.username == "testuser"
        assert user_dict.email == "testuser@example.com"
    
    def test_bad_user(self, session: Session):
        user.create(session, self.user_create)
        
        with pytest.raises(HTTPException) as exc_info:
            user.get(session, "testuser1")
        
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
        assert "User already exists in database" in str(exc_info.value.detail)
        
@pytest.fixture
def create_test_user(session: Session) -> tuple[str, str, SecretStr]:
    username = "testuser"
    email = "testuser@example.com"
    password = SecretStr("Test_1234!")
    obj_in = UserCreate(username=username, email=email, password=password)
    user.create(session, obj_in)
    return username, email, password

class TestAuthenticateUser:
    def test_auth_user(self, session: Session, create_test_user: tuple[str, str, SecretStr]):
        username, email, password = create_test_user
        
        user_obj = user.authenticate(session, username, password.get_secret_value())
        
        assert user_obj.username == username
        assert user_obj.email == email
        assert isinstance(user_obj.last_signed_in, datetime.datetime)
        assert user_obj.id is not None
        
    def test_bad_password(self, session: Session, create_test_user: tuple[str, str, SecretStr]):
        username, email, password = create_test_user
        
        with pytest.raises(HTTPException) as exc_info:
            user.authenticate(session, username, password="test_1234")
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Unauthorized"
        assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}
        
    def test_bad_username(self, session: Session, create_test_user: tuple[str, str, SecretStr]):
        username, email, password = create_test_user

        with pytest.raises(HTTPException) as exc_info:
            user.authenticate(session, username="test", password=password.get_secret_value())

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "User not found"
