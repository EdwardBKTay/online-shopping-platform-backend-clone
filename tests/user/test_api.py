import pytest
from tests.test_main import client_fixture, session_fixture
from fastapi.testclient import TestClient
from user.crud import user
from user.schema import UserCreate
from sqlmodel import Session
from pydantic import SecretStr
from utils.token_schema import TokenPayload, Token
from auth.auth import ACCESS_TOKEN_EXPIRATION_MINUTES, create_access_token, private_key
import datetime

class TestGetUserAPI:
    def test_api_working(self, client: TestClient, session: Session):
        user.create(session, UserCreate(username="testuser", email="testuser@example.com", password=SecretStr("Test&@1234!")))
        
        token_payload = TokenPayload(username="testuser", email="testuser@example.com", exp=datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRATION_MINUTES))
        token = create_access_token(token_payload, private_key)
        
        # Test Case 1: test api working
        response = client.get("/users/me/", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"


