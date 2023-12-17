import pytest
from db.models import User

from tests.test_main import client_fixture, session_fixture
from fastapi.testclient import TestClient
from services.user import user
from schemas.user import UserCreate
from sqlmodel import Session
from pydantic import SecretStr

@pytest.fixture
def login_user(client: TestClient, session: Session) -> tuple[str, User]:
    user_obj = UserCreate(username="testuser", email="testuser@example.com", password=SecretStr("Test_1234!"))
    
    user_dict = user.create(session, user_obj)
    
    data = client.post("/users/login", data={
        "username": "testuser",
        "password": "Test_1234!"
    })
    
    access_token = data.json()["access_token"]
    
    return access_token, user_dict

def test_get_username_existing_user(client: TestClient, session: Session, login_user: tuple[str, User]):
    token, user_dict = login_user
    
    response = client.get(f"/users/{user_dict.username}", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    assert response.json()["username"] == user_dict.username
    assert response.json()["email"] == user_dict.email
    assert "created_at" in response.json() and response.json()["created_at"] is not None
    assert "last_signed_in" in response.json() and response.json()["last_signed_in"] is not None
    assert "auth_token" in response.json() and response.json()["auth_token"] is not None
    assert "is_vendor" in response.json() and response.json()["is_vendor"] is False
    assert "is_superuser" in response.json() and response.json()["is_superuser"] is False
    
def test_get_username_without_token(client: TestClient):
    response = client.get("/users/test")
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated" 
    
def test_get_username_with_invalid_token(client: TestClient, session: Session, login_user: tuple[str, User]):
    token, user_dict = login_user
    
    response = client.get(f"/users/{user_dict.username}", headers={
        "Authorization": f"Bearer {token}abc"
    })
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"

@pytest.fixture
def test_data():
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "Test_1234!",
        "is_vendor": False,
        "is_superuser": False
    }
    
def test_post_create_user(client: TestClient, session: Session, test_data: dict):
    response = client.post("/users/create", json=test_data, headers={"Content-Type": "application/json"})
    
    assert response.status_code == 201
    assert response.json()["username"] == test_data["username"]
    assert response.json()["email"] == test_data["email"]
    assert "created_at" in response.json() and response.json()["created_at"] is not None
    assert "last_signed_in" in response.json() and response.json()["last_signed_in"] is None
    
def test_post_create_user_with_existing_username(client: TestClient, session: Session, test_data: dict):
    client.post("/users/create", json=test_data, headers={"Content-Type": "application/json"})
    
    response = client.post("/users/create", json=test_data, headers={"Content-Type": "application/json"})
    
    assert response.status_code == 409
    assert response.json()["detail"] == "User already exists"
    
def test_post_create_user_with_existing_email(client: TestClient, session: Session, test_data: dict):
    client.post("/users/create", json=test_data, headers={"Content-Type": "application/json"})
    
    test_data["username"] = "testuser2"
    
    response = client.post("/users/create", json=test_data, headers={"Content-Type": "application/json"})
    
    assert response.status_code == 409
    assert response.json()["detail"] == "User already exists"
    
def test_post_login_user(client: TestClient, session: Session, test_data: dict):
    client.post("/users/create", json=test_data, headers={"Content-Type": "application/json"})
    
    response = client.post("/users/login", data={
        "username": test_data["username"],
        "password": test_data["password"]
    })
    
    assert response.status_code == 200
    assert "access_token" in response.json() and "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"
    
def test_post_login_user_with_invalid_username(client: TestClient, session: Session, test_data: dict):
    client.post("/users/create", json=test_data, headers={"Content-Type": "application/json"})
    
    response = client.post("/users/login", data={
        "username": "testuser2",
        "password": test_data["password"]
    })
    
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
    
def test_post_login_user_with_invalid_password(client: TestClient, session: Session, test_data: dict):
    client.post("/users/create", json=test_data, headers={"Content-Type": "application/json"})
    
    response = client.post("/users/login", data={
        "username": test_data["username"],
        "password": "Test_1234"
    })
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid user credentials"
    
def test_logout_user(client: TestClient, session: Session, login_user: tuple[str, User]):
    token, user_dict = login_user
    
    response = client.get("/users/logout", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    assert response.json()["message"] == "User logged out successfully"
    assert response.headers["Authorization"] == ""
    
def test_logout_user_without_token(client: TestClient):
    response = client.get("/users/logout")
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_logout_user_with_invalid_token(client: TestClient, session: Session, login_user: tuple[str, User]):
    token, user_dict = login_user
    
    response = client.get("/users/logout", headers={
        "Authorization": f"Bearer {token}abc"
    })
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"
