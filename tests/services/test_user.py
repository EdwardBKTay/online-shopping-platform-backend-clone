import pytest

from db.models import User
from schemas.user import UserCreate, UserState
from pydantic import SecretStr
from sqlmodel import Session
from fastapi import HTTPException, status
from services.crud_user import user, get_current_user
from tests.test_main import session_fixture
from auth.auth import public_key, create_access_token, private_key
import datetime

class TestCRUDUser:
    @pytest.fixture
    def user_data(self) -> UserCreate:
        user_data = UserCreate(username="testuser", email="testuser@example.com", password=SecretStr("Test_1234!"))
        
        return user_data
    
    def test_get_username_existing_user(self, session: Session, user_data: UserCreate):
        # Test Case 1: To get user in db
        user_obj = user.create(session, user_data)
        user_dict = user.get_username(session, user_obj.username)
        
        if user_dict is None:
            pytest.fail("User not found")
        
        assert user_dict.username == "testuser"
        assert user_dict.email == "testuser@example.com"
        
    def test_get_username_nonexistent_user(self, session: Session):
        with pytest.raises(HTTPException) as exc_info:
            user.get_username(session, "testuser")
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "User not found"
        
    def test_get_username_invalid_username(self, session: Session):
        with pytest.raises(HTTPException) as exc_info:
            user.get_username(session, "testuser1")
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "User not found"
        
    def test_create_user(self, session: Session, user_data: UserCreate):
        # Test Case 1: Create a new user
        user_obj = user.create(session, user_data)
        assert user_obj.username == "testuser"
        assert user_obj.password_hash != "Test_1234!"
        assert isinstance(user_obj.created_at, datetime.datetime)
        
    def test_create_existing_username(self, session: Session, user_data: UserCreate):
        user.create(session, user_data)

        with pytest.raises(HTTPException) as exc_info:
            user.create(session, user_data)
    
        assert exc_info.value.status_code == status.HTTP_409_CONFLICT
        assert "User already exists" in str(exc_info.value.detail)
        
    def test_create_existing_email(self, session: Session, user_data: UserCreate):
        user.create(session, user_data)

        with pytest.raises(HTTPException) as exc_info:
            user.create(session, user_data)
    
        assert exc_info.value.status_code == status.HTTP_409_CONFLICT
        assert "User already exists" in str(exc_info.value.detail)
        
    @pytest.fixture
    def create_test_user(self, session: Session, user_data: UserCreate):
        user_obj = user.create(session, user_data)
        payload = UserState(username=user_obj.username, email=user_obj.email, is_vendor=user_obj.is_vendor, is_superuser=user_obj.is_superuser, exp=datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15))
        token = create_access_token(payload, private_key)
        user_obj.auth_token = token
        session.add(user_obj)
        session.commit()
        session.refresh(user_obj)
        
        return user_obj, token
        
    def test_get_current_user(self, session: Session, create_test_user: tuple[User, str]):
        user_obj, token = create_test_user
        
        user_dict = get_current_user(public_key, token, session)
        print(user_dict)
        
        if user_dict is None:
            pytest.fail("User not found")
        
        assert user_dict.username == user_obj.username
        assert user_dict.email == user_obj.email
        assert user_dict.id is not None
        
    def test_get_current_user_bad_token(self, session: Session, create_test_user: tuple[User, str]):
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(public_key, "bad_token", session)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid authentication credentials"
        
    def test_get_current_user_expired_token(self, session: Session, user_data: UserCreate):
        user_obj = user.create(session, user_data)
        
        payload = UserState(username=user_obj.username, email=user_obj.email, is_vendor=user_obj.is_vendor, is_superuser=user_obj.is_superuser, exp=datetime.datetime.now(datetime.UTC) - datetime.timedelta(seconds=5))
        token = create_access_token(payload, private_key)
        user_obj.auth_token = token
        session.add(user_obj)
        session.commit()
        session.refresh(user_obj)
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(public_key, token, session)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Token has expired"
