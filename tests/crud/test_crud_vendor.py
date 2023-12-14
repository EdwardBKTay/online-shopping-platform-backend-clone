import pytest

from schemas.vendor import VendorCreate
from fastapi import HTTPException, status
from crud.crud_vendor import vendor
from pydantic import SecretStr
from sqlmodel import Session
from tests.test_main import session_fixture
import datetime

class TestGetVendorByUsername:
    vendor_create = VendorCreate(username="testuser", email="testuser@example.com", password=SecretStr("Test)1234!"))
    
    def test_get_vendor(self, session: Session):
        vendor_obj = vendor.create(session, self.vendor_create)
        vendor_dict = vendor.get(session,vendor_obj.username)
        
        assert vendor_dict.username == "testuser"
        assert vendor_dict.email == "testuser@example.com"
        
    def test_bad_vendor(self, session: Session):
        vendor.create(session, self.vendor_create)
        
        with pytest.raises(HTTPException) as exc_info:
            vendor.get(session, "testuser1")
            
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Not found"

class TestCreateVendor:
    def test_create_new_vendor(self, session: Session):
        vendor_create = VendorCreate(username="testuser", email="testuser@example.com", password=SecretStr("Test_1234!"))
        vendor_obj = vendor.create(session, vendor_create)
        assert vendor_obj.username == "testuser"
        assert vendor_obj.password_hash != "Test_1234!"
        assert isinstance(vendor_obj.created_at, datetime.datetime)
        
    def test_existing_username(self, session: Session):
        vendor_create1 = VendorCreate(username="testuser1", email="testuser1@example.com", password=SecretStr("Test_1234!"))
        vendor.create(session, vendor_create1)
        
        with pytest.raises(HTTPException) as exc_info:
            vendor_create2 = VendorCreate(username="testuser1", email="testuser2@example.com", password=SecretStr("Test_5678!"))
            vendor.create(session, vendor_create2)
            
        assert exc_info.value.status_code == status.HTTP_409_CONFLICT
        assert "User already exists in database" in str(exc_info.value.detail)

@pytest.fixture
def create_test_vendor(session: Session) -> tuple[str, str, SecretStr]:
    username="testuser"
    email="testuser@example.com"
    password=SecretStr("Test_1234!")
    obj_in = VendorCreate(username=username, email=email, password=password)
    vendor.create(session, obj_in)
    return username, email, password

class TestAuthenticateVendor:
    def test_auth_vendor(self, session: Session, create_test_vendor:  tuple[str, str, SecretStr]):
        username, email, password = create_test_vendor
        vendor_obj = vendor.authenticate(session, username, password.get_secret_value())
        assert vendor_obj.username == username
        assert vendor_obj.email == email
        assert isinstance(vendor_obj.last_signed_in, datetime.datetime)
        assert vendor_obj.last_signed_in > vendor_obj.created_at
        assert vendor_obj.id is not None
        
    def test_bad_password(self, session: Session, create_test_vendor: tuple[str, str, SecretStr]):
        username, email, password = create_test_vendor
        
        with pytest.raises(HTTPException) as exc_info:
            vendor.authenticate(session, username, "BadPassword")
            
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Unauthorized"
        assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}
        
    def test_bad_username(self, session: Session, create_test_vendor: tuple[str, str, SecretStr]):
        username, email, password = create_test_vendor
        
        with pytest.raises(HTTPException) as exc_info:
            vendor.authenticate(session, "BadUsername", password.get_secret_value())
            
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Not found"
