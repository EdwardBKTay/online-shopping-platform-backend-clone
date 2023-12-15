from fastapi import HTTPException, status
import pytest

from core.deps import get_session, get_current_entity
from auth.auth import create_access_token
from tests.test_main import session_fixture
from tests.crud.test_crud_user import create_test_user
from crud.crud_user import user
from schemas.token import TokenPayload
from db.models import User
from sqlmodel import Session
import datetime

def test_get_session():
    session = get_session()
    
    assert session is not None
    
@pytest.fixture
def token_fixture(create_test_user):
    username, email, password = create_test_user
    token_payload = TokenPayload(username=username, email=email, exp=datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15))
    token = create_access_token(token_payload)
    return token

class TestGetCurrentEntity:
    def test_get_current_entity(self, token_fixture, session: Session):
        token = token_fixture
        decoded_token = get_current_entity(token, session)
        
        assert decoded_token.username == "testuser"
        assert decoded_token.email == "testuser@example.com"
        
    def test_bad_token(self, token_fixture, session: Session):
        token = token_fixture + "a"
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_entity(token, session)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Invalid authentication credentials"
