import pytest

from tests.test_main import client_fixture, session_fixture
from fastapi.testclient import TestClient
from sqlmodel import Session
from schemas.user import UserCreate
from db.models import User
from schemas.product import ProductCreate, ProductUpdate
from pydantic import SecretStr
from services.crud_user import user

@pytest.fixture
def login_vendor(client: TestClient, session: Session):
    user_obj = UserCreate(username="testvendor", email="testvendor@example.com", password=SecretStr("Test_1234!"), is_vendor=True)
    
    user_dict = user.create(session, user_obj)
    
    data = client.post("/users/login", data={
        "username": "testvendor",
        "password": "Test_1234!"
    })
    
    access_token = data.json()["access_token"]
    
    return access_token, user_dict

def test_create_product(client: TestClient, session: Session, login_vendor: tuple[str, User]):
    token, user_dict = login_vendor
    
    product_obj = ProductCreate(name="Test New Product", description="Test Product Description", price=10.00, quantity=10)
    
    response = client.post("/products/create/", json={
        "name": "Test New Product",
        "description": "Test Product Description",
        "price": 10.00,
        "quantity": 10
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 201
    assert response.json()["name"] == product_obj.name
    assert response.json()["description"] == product_obj.description
    assert response.json()["price"] == product_obj.price
    assert response.json()["quantity"] == product_obj.quantity
    assert response.json()["vendor_id"] == user_dict.id
    assert "created_at" in response.json() and response.json()["created_at"] is not None
    assert "updated_at" in response.json() and response.json()["updated_at"] is None

@pytest.fixture
def create_product(client: TestClient, session: Session, login_vendor: tuple[str, User]):
    product_obj = ProductCreate(name="Test Product", description="Test Product Description", price=10.00, quantity=10)
    
    data = client.post("/products/create/", json=product_obj.model_dump(), headers={
        "Authorization": f"Bearer {login_vendor[0]}"
    })
    
    return data.json()

def test_create_product_without_token(client: TestClient, session: Session):
    product_obj = ProductCreate(name="Test Product", description="Test Product Description", price=10.00, quantity=10)
    
    response = client.post("/products/create/", json=product_obj.model_dump())
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_create_product_with_invalid_token(client: TestClient, session: Session, login_vendor: tuple[str, User]):
    token, user_dict = login_vendor
    
    product_obj = ProductCreate(name="Test Product", description="Test Product Description", price=10.00, quantity=10)
    
    response = client.post("/products/create/", json=product_obj.model_dump(), headers={
        "Authorization": f"Bearer {token}abc"
    })
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"
    
def test_create_duplicated_product(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict):
    token, user_dict = login_vendor
    
    product_obj = ProductCreate(name="Test Product", description="Test Product Description", price=10.00, quantity=10)
    
    response = client.post("/products/create/", json=product_obj.model_dump(), headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 409
    assert response.json()["detail"] == "Product name duplicated"

def test_update_product(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict):
    token, user_dict = login_vendor
    
    product_obj = ProductUpdate(name="Test Product Updated", description="Test Product Description Updated", price=20.00, quantity=20)
    
    response = client.put(f"/products/{create_product['id']}/update/", json=product_obj.model_dump(exclude_unset=True), headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    assert response.json()["name"] == product_obj.name
    assert response.json()["description"] == product_obj.description
    assert response.json()["price"] == product_obj.price
    assert response.json()["quantity"] == product_obj.quantity
    assert response.json()["vendor_id"] == user_dict.id
    assert response.json()["created_at"] == create_product["created_at"]
    assert "updated_at" in response.json() and response.json()["updated_at"] is not None

def test_partial_update_product(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict):
    token, user_dict = login_vendor
    
    product_obj = ProductUpdate(name="Test Updated Product")
    
    response = client.put(f"/products/{create_product['id']}/update/", json=product_obj.model_dump(exclude_unset=True), headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    assert response.json()["name"] == product_obj.name
    assert response.json()["description"] == create_product["description"]
    assert response.json()["price"] == create_product["price"]
    assert response.json()["quantity"] == create_product["quantity"]
    assert response.json()["vendor_id"] == user_dict.id
    assert response.json()["created_at"] == create_product["created_at"]
    assert "updated_at" in response.json() and response.json()["updated_at"] is not None

def test_delete_product(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict):
    token, user_dict = login_vendor
    
    response = client.delete(f"/products/{create_product['id']}/delete/", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    assert response.json()["message"] == "Product deleted successfully"

def test_delete_unknown_product(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict):
    token, user_dict = login_vendor
    
    response = client.delete("/products/99/delete/", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

def test_delete_product_unauthorized(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict):
    token, user_dict = login_vendor
    
    user_obj = UserCreate(username="testuser", email="testuser@example.com", password=SecretStr("Test_1234!"), is_vendor=True)
    
    user_dict = user.create(session, user_obj)
    
    data = client.post("/users/login", data={
        "username": "testuser",
        "password": "Test_1234!"
    })
    
    access_token = data.json()["access_token"]
    
    response = client.delete(f"/products/{create_product['id']}/delete/", headers={
        "Authorization": f"Bearer {access_token}"
    })
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Unauthorized to delete product"

def test_get_product(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict):
    response = client.get(f"/products/{create_product['id']}/", headers={
        "Authorization": f"Bearer {login_vendor[0]}"
    })
    
    assert response.status_code == 200
    assert response.json()["name"] == create_product["name"]
    assert response.json()["description"] == create_product["description"]
    assert response.json()["price"] == create_product["price"]
    assert response.json()["quantity"] == create_product["quantity"]
    assert response.json()["vendor_id"] == create_product["vendor_id"]
    assert response.json()["created_at"] == create_product["created_at"]
    assert response.json()["updated_at"] == create_product["updated_at"]
    
def test_get_product_as_user(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict):
    user_obj = UserCreate(username="testuser", email="testuse@example.com", password=SecretStr("Test_1234!"))
    
    user.create(session, user_obj)
    
    data = client.post("/users/login", data={
        "username": "testuser",
        "password": "Test_1234!"
    })
    
    access_token = data.json()["access_token"]
    
    response = client.get(f"/products/{create_product['id']}/", headers={
        "Authorization": f"Bearer {access_token}"
    })
    
    assert response.status_code == 200
    assert response.json()["name"] == create_product["name"]
    assert response.json()["description"] == create_product["description"]
    assert response.json()["price"] == create_product["price"]
    assert response.json()["quantity"] == create_product["quantity"]
    assert response.json()["vendor_id"] == create_product["vendor_id"]
    assert response.json()["created_at"] == create_product["created_at"]
    assert response.json()["updated_at"] == create_product["updated_at"]

def test_get_unknown_product(client: TestClient, session: Session, login_vendor: tuple[str, User]):
    response = client.get("/products/99/", headers={
        "Authorization": f"Bearer {login_vendor[0]}"
    })
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"
