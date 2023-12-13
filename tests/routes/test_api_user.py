import pytest

from tests.test_main import client_fixture, session_fixture
from fastapi.testclient import TestClient

class TestGetUserByUsernameAPI:
    def setup_user(self, client: TestClient):
        client.post("/users/create/", data={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "Test&@1234!"
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        
        client.post("/token/", data={
            "username": "testuser",
            "password": "Test&@1234!"
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        
    def test_api_working(self, client: TestClient):
        self.setup_user(client)
        
        response = client.get("/users/testuser/")
        
        data = response.json()
        
        assert response.status_code == 200
        assert data["username"] == "testuser"
        assert data["email"] == "testuser@example.com"
        assert data["id"] is not None
    
    def test_bad_username(self, client: TestClient):
        self.setup_user(client)
        
        response = client.get("/users/test/")
        
        data = response.json()
        
        assert response.status_code == 404
        assert "detail" in data and data["detail"] == "User not found"

class TestUserCreationAPI:
    def test_api_working(self, client: TestClient):
        # Test Case 1: test api working
        response = client.post("/users/create/", data={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "Test&@1234!"
        }, headers={"Content-Type": "application/x-www-form-urlencoded"}) # type: ignore
        
        response_data = response.json()
        
        assert response.status_code == 201
        assert "message" in response_data and response_data["message"] == "User has been created"
    
    def test_bad_username(self, client: TestClient):
        # Test Case 2: username having spaces
        response = client.post("/users/create/", data={
            "username": "test user",
            "email": "testuser@example.com",
            "password": "Test_12345!"
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        
        assert response.status_code == 400
        assert "Validation Error" in response.json()["detail"]
        
    def test_bad_email(self, client: TestClient):
        # Test Case 3: bad email
        response = client.post("/users/create/", data={
            "username": "testuser",
            "email": "testuser",
            "password": "Test_1234!"
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
                
        assert response.status_code == 422
        
    def test_bad_password(self, client: TestClient):
        # Test Case 4: bad password
        response = client.post("/users/create/", data={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "Test 1234"
        }, headers={"Content-Type": "application/x-www-form-urlencoded"}) # type: ignore
        
        assert response.status_code == 400

