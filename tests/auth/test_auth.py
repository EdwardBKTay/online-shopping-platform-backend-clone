import pytest

from auth.auth import get_password_hash, verify_password, create_access_token, read_private_key, read_public_key
from pydantic import SecretStr
from jose import jwt
from schemas.user import UserState
import datetime

def test_get_password_hash():
    password = "testpassword"
    password_hash = get_password_hash(password)
    
    assert isinstance(password_hash, str)
    assert password_hash != password
    
def test_verify_password():
    password = "testpassword"
    password_hash = get_password_hash(password)
    
    assert verify_password(password, password_hash)
    assert not verify_password("wrongpassword", password_hash)
    
def test_create_access_token():
    user_state = UserState(username="testuser", email="testuser@example.com", exp=datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15), is_vendor=False, is_superuser=False)
    
    access_token = create_access_token(user_state, read_private_key())
    
    decoded_token = jwt.decode(access_token, read_public_key(), algorithms=["RS256"])
    
    assert isinstance(access_token, str)
    assert user_state.username == decoded_token["username"]
    assert user_state.email == decoded_token["email"]
    if isinstance(user_state.exp, datetime.datetime):
        assert int(user_state.exp.timestamp()) == decoded_token["exp"]
    else:
        assert user_state.exp == decoded_token["exp"]
    assert user_state.is_vendor == decoded_token["is_vendor"]
    assert user_state.is_superuser == decoded_token["is_superuser"]
