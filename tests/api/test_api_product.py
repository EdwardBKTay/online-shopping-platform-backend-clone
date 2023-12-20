import pytest

from tests.test_main import client_fixture, session_fixture
from fastapi.testclient import TestClient
from sqlmodel import Session
from schemas.user import UserCreate
from db.models import User
from schemas.product import ProductCreate, ProductUpdate, ProductCategory
from pydantic import SecretStr
from services.crud_user import user
from decimal import Decimal
from typing import Any

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
    
    product_obj = ProductCreate(name="Test New Product", description="Test Product Description", original_price=Decimal(10), available_quantity=10, category_name=ProductCategory.others)
    
    response = client.post("/products/create/", json={
        "name": "Test New Product",
        "description": "Test Product Description",
        "original_price": 10,
        "available_quantity": 10,
        "category_name": "Others"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 201
    assert response.json()["name"] == product_obj.name
    assert response.json()["description"] == product_obj.description
    assert response.json()["original_price"] == str(product_obj.original_price)
    assert response.json()["available_quantity"] == product_obj.available_quantity
    assert response.json()["vendor_id"] == user_dict.id
    assert "created_at" in response.json() and response.json()["created_at"] is not None
    assert "updated_at" in response.json() and response.json()["updated_at"] is None
    
def test_create_product_without_token(client: TestClient, session: Session):
    product_obj = ProductCreate(name="Test New Product", description="Test Product Description", original_price=Decimal(10), available_quantity=10, category_name=ProductCategory.others)
    
    response = client.post("/products/create/", json={
        "name": "Test New Product",
        "description": "Test Product Description",
        "original_price": 10,
        "available_quantity": 10,
        "category_name": "Others"
    })
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    
def test_create_product_with_invalid_token(client: TestClient, session: Session, login_vendor: tuple[str, User]):
    token, user_dict = login_vendor
    
    product_obj = ProductCreate(name="Test New Product", description="Test Product Description", original_price=Decimal(10), available_quantity=10, category_name=ProductCategory.others)
    
    response = client.post("/products/create/", json={
        "name": "Test New Product",
        "description": "Test Product Description",
        "original_price": 10,
        "available_quantity": 10,
        "category_name": "Others"
    }, headers={
        "Authorization": f"Bearer {token}abc"
    })
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"
    
@pytest.fixture
def create_product(client: TestClient, login_vendor: tuple[str, User]) -> dict[str, Any]:
    token, user_dict = login_vendor
    
    data = client.post("/products/create/", json={
        "name": "Test Product",
        "description": "Test Product Description",
        "original_price": 10,
        "available_quantity": 10,
        "category_name": "Others"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    return data.json()
    
def test_create_duplicated_product(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict[str, Any]):
    token, user_dict = login_vendor
    
    response = client.post("/products/create/", json={
        "name": "Test Product",
        "description": "Test Product Description",
        "original_price": 10,
        "available_quantity": 10,
        "category_name": "Others"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 409
    assert response.json()["detail"] == "Product name duplicated"
    
def test_search_products(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict[str, Any]):
    token, user_dict = login_vendor
    
    response = client.get("/products/search/?product_name=Test&category=Others", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == create_product["name"]
    assert response.json()[0]["description"] == create_product["description"]
    assert response.json()[0]["original_price"] == str(create_product["original_price"])
    assert response.json()[0]["available_quantity"] == create_product["available_quantity"]
    assert response.json()[0]["vendor_id"] == create_product["vendor_id"]
    assert response.json()[0]["created_at"] == create_product["created_at"]
    assert response.json()[0]["updated_at"] == create_product["updated_at"]
    
def test_search_products_without_token(client: TestClient, session: Session, create_product: dict[str, Any]):
    response = client.get("/products/search/?product_name=Test&category=Others")
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    
def test_search_products_with_invalid_token(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict[str, Any]):
    token, user_dict = login_vendor
    
    response = client.get("/products/search/?product_name=Test&category=Others", headers={
        "Authorization": f"Bearer {token}abc"
    })
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"
    
def test_search_products_by_name(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict[str, Any]):
    token, user_dict = login_vendor
    
    response = client.get("/products/search/?product_name=Test", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == create_product["name"]
    assert response.json()[0]["description"] == create_product["description"]
    assert response.json()[0]["original_price"] == str(create_product["original_price"])
    assert response.json()[0]["available_quantity"] == create_product["available_quantity"]
    assert response.json()[0]["vendor_id"] == create_product["vendor_id"]
    assert response.json()[0]["created_at"] == create_product["created_at"]
    assert response.json()[0]["updated_at"] == create_product["updated_at"]
    
def test_search_products_by_category(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict[str, Any]):
    token, user_dict = login_vendor
    
    response = client.get("/products/search/?category=Others", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == create_product["name"]
    assert response.json()[0]["description"] == create_product["description"]
    assert response.json()[0]["original_price"] == str(create_product["original_price"])
    assert response.json()[0]["available_quantity"] == create_product["available_quantity"]
    assert response.json()[0]["vendor_id"] == create_product["vendor_id"]
    assert response.json()[0]["created_at"] == create_product["created_at"]
    assert response.json()[0]["updated_at"] == create_product["updated_at"]
    
def test_search_unknown_product(client: TestClient, session: Session, login_vendor: tuple[str, User]):
    token, user_dict = login_vendor
    
    response = client.get("/products/search/?product_name=Unknown", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    assert len(response.json()) == 0
    
def test_search_unknown_product_with_category(client: TestClient, session: Session, login_vendor: tuple[str, User]):
    token, user_dict = login_vendor
    
    response = client.get("/products/search/?product_name=Unknown&category=Others", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    assert len(response.json()) == 0
    
def test_get_category_products(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict[str, Any]):
    token, user_dict = login_vendor
    
    response = client.get("/products/category/?category=Others", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == create_product["name"]
    assert response.json()[0]["description"] == create_product["description"]
    assert response.json()[0]["original_price"] == str(create_product["original_price"])
    assert response.json()[0]["available_quantity"] == create_product["available_quantity"]
    assert response.json()[0]["vendor_id"] == create_product["vendor_id"]
    assert response.json()[0]["created_at"] == create_product["created_at"]
    assert response.json()[0]["updated_at"] == create_product["updated_at"]
    
def test_get_category_products_without_token(client: TestClient, session: Session, create_product: dict[str, Any]):
    response = client.get("/products/category/?category=Others")
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    
def test_get_category_products_with_invalid_token(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict[str, Any]):
    token, user_dict = login_vendor
    
    response = client.get("/products/category/?category=Others", headers={
        "Authorization": f"Bearer {token}abc"
    })
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"
    
def test_get_unknown_category_products(client: TestClient, session: Session, login_vendor: tuple[str, User]):
    token, user_dict = login_vendor
    
    response = client.get("/products/category/?category=Unknown", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"

def test_update_product(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict[str, Any]):
    token, user_dict = login_vendor
    
    product_obj = ProductUpdate(name="Test Product Updated", description="Test Product Description Updated", original_price=Decimal(20), available_quantity=20, category_name=ProductCategory.others)
    
    response = client.put(f"/products/{create_product['id']}/update/", json={
        "name": "Test Product Updated",
        "description": "Test Product Description Updated",
        "original_price": 20,
        "available_quantity": 20,
        "category_name": "Others"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    assert response.json()["name"] == product_obj.name
    assert response.json()["description"] == product_obj.description
    assert response.json()["original_price"] == str(product_obj.original_price)
    assert response.json()["available_quantity"] == product_obj.available_quantity
    assert response.json()["vendor_id"] == user_dict.id
    assert response.json()["created_at"] == create_product["created_at"]
    assert "updated_at" in response.json() and response.json()["updated_at"] is not None

def test_partial_update_product(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict[str, Any]):
    token, user_dict = login_vendor
    
    product_obj = ProductUpdate(name="Test Updated Product")
    
    response = client.put(f"/products/{create_product['id']}/update/", json={
        "name": "Test Updated Product"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    assert response.json()["name"] == product_obj.name
    assert response.json()["description"] == create_product["description"]
    assert response.json()["original_price"] == str(create_product["original_price"])
    assert response.json()["available_quantity"] == create_product["available_quantity"]
    assert response.json()["vendor_id"] == user_dict.id
    assert response.json()["created_at"] == create_product["created_at"]
    assert "updated_at" in response.json() and response.json()["updated_at"] is not None
    
def test_update_product_without_token(client: TestClient, session: Session, create_product: dict[str, Any]):
    response = client.put(f"/products/{create_product['id']}/update/", json={
        "name": "Test Product Updated",
        "description": "Test Product Description Updated",
        "original_price": 20,
        "available_quantity": 20,
        "category_name": "Others"
    })
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    
def test_update_product_with_invalid_token(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict[str, Any]):
    token, user_dict = login_vendor
    
    response = client.put(f"/products/{create_product['id']}/update/", json={
        "name": "Test Product Updated",
        "description": "Test Product Description Updated",
        "original_price": 20,
        "available_quantity": 20,
        "category_name": "Others"
    }, headers={
        "Authorization": f"Bearer {token}abc"
    })
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"
    
def test_update_unknown_product(client: TestClient, session: Session, login_vendor: tuple[str, User]):
    token, user_dict = login_vendor
    
    response = client.put("/products/99/update/", json={
        "name": "Test Product Updated",
        "description": "Test Product Description Updated",
        "original_price": 20,
        "available_quantity": 20,
        "category_name": "Others"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"
    
def test_update_product_as_user(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict[str, Any]):
    user_obj = UserCreate(username="testuser", email="testuser@example.com", password=SecretStr("Test_1234!"))
    
    user.create(session, user_obj)
    
    data = client.post("/users/login", data={
        "username": "testuser",
        "password": "Test_1234!"
    })
    
    access_token = data.json()["access_token"]
    
    response = client.put(f"/products/{create_product['id']}/update/", json={
        "name": "Test Product Updated",
        "description": "Test Product Description Updated",
        "original_price": 20,
        "available_quantity": 20,
        "category_name": "Others"
    }, headers={
        "Authorization": f"Bearer {access_token}"
    })
    
    assert response.status_code == 403
    assert response.json()["detail"] == "User is not a vendor"
    
def test_update_product_as_other_vendor(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict[str, Any]):
    user_obj = UserCreate(username="testvendor2", email="testvendor2@example.com", password=SecretStr("Test_1234!"), is_vendor=True)
    
    user.create(session, user_obj)
    
    data = client.post("/users/login", data={
        "username": "testvendor2",
        "password": "Test_1234!"
    })
    
    access_token = data.json()["access_token"]
    
    response = client.put(f"/products/{create_product['id']}/update/", json={
        "name": "Test Product Updated",
        "description": "Test Product Description Updated",
        "original_price": 20,
        "available_quantity": 20,
        "category_name": "Others"
    }, headers={
        "Authorization": f"Bearer {access_token}"
    })
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Unauthorized to update product"

def test_delete_product(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict[str, Any]):
    token, user_dict = login_vendor
    
    response = client.delete(f"/products/{create_product['id']}/delete/", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 204
    
def test_delete_unknown_product(client: TestClient, session: Session, login_vendor: tuple[str, User]):
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
    assert response.json()["original_price"] == create_product["original_price"]
    assert response.json()["available_quantity"] == create_product["available_quantity"]
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
    assert response.json()["original_price"] == create_product["original_price"]
    assert response.json()["available_quantity"] == create_product["available_quantity"]
    assert response.json()["vendor_id"] == create_product["vendor_id"]
    assert response.json()["created_at"] == create_product["created_at"]
    assert response.json()["updated_at"] == create_product["updated_at"]

def test_get_unknown_product(client: TestClient, session: Session, login_vendor: tuple[str, User]):
    response = client.get("/products/99/", headers={
        "Authorization": f"Bearer {login_vendor[0]}"
    })
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

def test_get_all_products(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict[str, Any]):
    response = client.get("/products/", headers={
        "Authorization": f"Bearer {login_vendor[0]}"
    })
    
    assert response.status_code == 200
    assert len(response.json()) == 1

