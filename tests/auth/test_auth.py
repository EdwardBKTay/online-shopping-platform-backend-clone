import pytest

from auth.auth import get_password_hash, verify_password, create_access_token, private_key, public_key
from pydantic import SecretStr
from jose import jwt
from schemas.user import UserState
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
        payload = UserState(username="testuser", email="testuser@example.com", exp=datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15))
        access_token = create_access_token(payload, private_key)
        decoded_token = jwt.decode(access_token, public_key, algorithms=["RS256"])
        
        assert isinstance(access_token, str)
        assert payload.username == decoded_token["username"]
        assert payload.email == decoded_token["email"]
        if isinstance(payload.exp, datetime.datetime):
            assert int(payload.exp.timestamp()) == decoded_token["exp"]
        else:
            assert payload.exp == decoded_token["exp"]
        assert payload.is_vendor == decoded_token["is_vendor"]
