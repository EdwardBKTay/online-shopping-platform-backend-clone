import pytest

from auth.auth import get_password_hash, verify_password, create_access_token
from pydantic import SecretStr

from schemas.token import TokenPayload
import datetime

class TestPasswordHash:
    pwd = SecretStr("Test_1234!")
    
    def test_password(self):
        # test encrypt and decrypt of password
        pwd_hash = get_password_hash(self.pwd.get_secret_value())
        is_pwd = verify_password(self.pwd.get_secret_value(), pwd_hash)
        
        assert is_pwd == True
        
    def test_wrong_password(self):
        pwd = SecretStr("Test_1234!")
        pwd_hash = get_password_hash(str(pwd))
        is_pwd = verify_password(str(pwd), pwd_hash)
        
        assert is_pwd == True

class TestCreateAccessToken:
    def test_create(self):
        payload: TokenPayload = TokenPayload(username="testuser", email="testuser@example.com", exp=datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15))
        access_token = create_access_token(payload)
        
        assert isinstance(access_token, str)
