import pytest

from tests.test_main import client_fixture, session_fixture
from fastapi.testclient import TestClient
from services.user import user
from schemas.user import UserCreate
from sqlmodel import Session
from pydantic import SecretStr

class TestGetUserAPI:
    def test_api_working(self, client: TestClient, session: Session):
        user_obj = UserCreate(username="testuser", email="testuser@example.com", password=SecretStr("Test&@1234!"), is_vendor=False)
        
        user.create(session, user_obj)
        
        data = client.post("/users/login", data={
            "username": "testuser",
            "password": "Test&@1234!"
        })
        
        response = client.get("/users/", headers={
            "Authorization": f"Bearer {data.json()['access_token']}"
        })
        
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"
        assert response.json()["email"] == "testuser@example.com"
        
    def test_api_not_working(self, client: TestClient):
        response = client.get("/users/")
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

class TestUserCreationAPI:
    def test_api_working(self, client: TestClient):
        # Test Case 1: test api working
        response = client.post("/users/create/", json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "Test&@1234!",
            "is_vendor": False
        }, headers={"Content-Type": "application/json"})
        
        response_data = response.json()
        
        assert response.status_code == 201
        assert response_data["username"] == "testuser"
        assert response_data["email"] == "testuser@example.com"
        assert "created_at" in response_data and response_data["created_at"] is not None
        
    def test_bad_username(self, client: TestClient):
        # Test Case 2: username having spaces
        response = client.post("/users/create/", json={
            "username": "test user",
            "email": "testuser@example.com",
            "password": "Test_12345!",
            "is_vendor": False
        }, headers={"Content-Type": "application/json"})
        
        assert response.status_code == 422
        
    def test_bad_email(self, client: TestClient):
        # Test Case 3: bad email
        response = client.post("/users/create/", json={
            "username": "testuser",
            "email": "testuser",
            "password": "Test_1234!",
            "is_vendor": False
        }, headers={"Content-Type": "application/json"})
        
        assert response.status_code == 422
        
    def test_bad_password(self, client: TestClient):
        # Test Case 4: bad password
        response = client.post("/users/create/", json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "Test 1234",
            "is_vendor": False
        }, headers={"Content-Type": "application/json"})
        
        assert response.status_code == 422

class TestUserLoginAPI:
    def test_api_working(self, client: TestClient):
        # Test Case 1: test api working
        client.post("/users/create/", json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "Test&@1234!",
            "is_vendor": False
        }, headers={"Content-Type": "application/json"})
        
        response = client.post("/users/login/", data={
            "username": "testuser",
            "password": "Test&@1234!"
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        
        data = response.json()
        
        assert response.status_code == 200
        assert "access_token" in data and "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_user_not_found(self, client: TestClient):
        # Test Case 2: user not found
        response = client.post("/users/login/", data={
            "username": "testuser",
            "password": "Test&@1234!"
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"
