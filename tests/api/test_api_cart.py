import pytest

from tests.test_main import client_fixture, session_fixture
from fastapi.testclient import TestClient
from schemas.user import UserCreate
from sqlmodel import Session
from services.crud_user import user
from db.models import User, Cart
from schemas.cart import CartCreate, CartUpdate
from pydantic import SecretStr
from tests.api.test_api_product import create_product, login_vendor
from tests.api.test_api_user import login_user

def test_add_to_cart(client: TestClient, session: Session, login_user: tuple[str, User], create_product: dict):
    token, user_dict = login_user
    
    response = client.post(f"/carts/{user_dict.username}/add/{create_product["id"]}", json={
        "quantity": 5
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 201
    assert response.json()["product_id"] == create_product["id"]
    assert response.json()["quantity"] == 5
    assert response.json()["cart_id"] is not None
    assert response.json()["created_at"] is not None
    assert response.json()["updated_at"] is None
    
def test_add_to_cart_without_token(client: TestClient, session: Session, create_product: dict):
    response = client.post(f"/carts/testuser/add/{create_product["id"]}", json={
        "quantity": 5
    })
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    
def test_add_to_cart_not_user(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict):
    token, user_dict = login_vendor
    
    response = client.post(f"/carts/{user_dict.username}/add/{create_product["id"]}", json={
        "quantity": 5
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 403
    assert response.json()["detail"] == "User is not a customer"
    
def test_add_to_cart_invalid_product(client: TestClient, session: Session, login_user: tuple[str, User]):
    token, user_dict = login_user
    
    response = client.post(f"/carts/{user_dict.username}/add/999", json={
        "quantity": 5
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"
    
def test_add_to_cart_not_enough_stock(client: TestClient, session: Session, login_user: tuple[str, User], create_product: dict):
    token, user_dict = login_user
    
    response = client.post(f"/carts/{user_dict.username}/add/{create_product["id"]}", json={
        "quantity": 999
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 409
    assert response.json()["detail"] == "Not enough stock"

def test_add_to_cart_duplicated_product(client: TestClient, session: Session, login_user: tuple[str, User], create_product: dict):
    token, user_dict = login_user
    
    client.post(f"/carts/{user_dict.username}/add/{create_product["id"]}", json={
        "quantity": 5
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    response = client.post(f"/carts/{user_dict.username}/add/{create_product["id"]}", json={
        "quantity": 5
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 409
    assert response.json()["detail"] == "Product already in cart"
    
def test_add_to_cart_not_cart_owner(client: TestClient, session: Session, login_user: tuple[str, User], create_product: dict):
    token, user_dict = login_user
    
    new_user = user.create(session, UserCreate(username="testuser2", email="testuser2@example.com", password=SecretStr('Test_1234!')))
    
    data = client.post("/users/login", data={
        "username": "testuser2",
        "password": "Test_1234!"
    })
    
    access_token = data.json()["access_token"]
    
    response = client.post(f"/carts/{user_dict.username}/add/{create_product["id"]}", json={
        "quantity": 5
    }, headers={
        "Authorization": f"Bearer {access_token}"
    })
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Unauthorized to add to other user's cart"
    
@pytest.fixture
def add_items_to_cart(client: TestClient, session: Session, login_user: tuple[str, User], create_product: dict) -> tuple[str, Cart, User]:
    token, user_dict = login_user
    
    cart_data = client.post("/carts/testuser/add/1", json={
        "quantity": 5
    }, headers={
        "Authorization": f"Bearer {token}"
    }).json()
    
    return token, cart_data, user_dict

def test_get_user_cart(client: TestClient, session: Session, add_items_to_cart: tuple[str, Cart, User]):
    token, cart_data, user_dict = add_items_to_cart
    
    response = client.get(f"/carts/{user_dict.username}/", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["product_id"] == cart_data["product_id"]
    assert response.json()[0]["quantity"] == cart_data["quantity"]
    assert response.json()[0]["cart_id"] == cart_data["cart_id"]
    assert response.json()[0]["created_at"] is not None
    assert response.json()[0]["updated_at"] is None
    
def test_get_user_cart_without_token(client: TestClient, session: Session, add_items_to_cart: tuple[str, Cart, User]):
    token, cart_data, user_dict = add_items_to_cart
    
    response = client.get(f"/carts/{user_dict.username}/")
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    
def test_get_user_cart_not_user(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict):
    token, user_dict = login_vendor
    
    response = client.get(f"/carts/{user_dict.username}/", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 403
    assert response.json()["detail"] == "User is not a customer"
    
def test_get_user_cart_not_cart_owner(client: TestClient, session: Session, add_items_to_cart: tuple[str, Cart, User]):
    token, cart_data, user_dict = add_items_to_cart
    
    new_user = user.create(session, UserCreate(username="testuser2", email="testuser2@example.com", password=SecretStr('Test_1234!')))
    
    data = client.post("/users/login", data={
        "username": "testuser2",
        "password": "Test_1234!"
    })
    
    access_token = data.json()["access_token"]
    
    response = client.get(f"/carts/{user_dict.username}/", headers={
        "Authorization": f"Bearer {access_token}"
    })
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Unauthorized to view other user's cart"
    
def test_update_cart_items(client: TestClient, session: Session, add_items_to_cart: tuple[str, Cart, User]):
    token, cart_data, user_dict = add_items_to_cart
    
    response = client.put(f"/carts/{user_dict.username}/{cart_data['cart_id']}/update", json={
        "quantity": 3
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    assert response.json()["product_id"] == cart_data["product_id"]
    assert response.json()["quantity"] == 3
    assert response.json()["cart_id"] == cart_data["cart_id"]
    assert response.json()["created_at"] is not None
    assert response.json()["updated_at"] is not None

def test_update_cart_items_without_token(client: TestClient, session: Session, add_items_to_cart: tuple[str, Cart, User]):
    token, cart_data, user_dict = add_items_to_cart
    
    response = client.put(f"/carts/{user_dict.username}/{cart_data['cart_id']}/update", json={
        "quantity": 3
    })
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    
def test_update_cart_items_not_user(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict):
    token, user_dict = login_vendor
    
    response = client.put(f"/carts/{user_dict.username}/1/update", json={
        "quantity": 3
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 403
    assert response.json()["detail"] == "User is not a customer"
    
    
def test_update_cart_items_not_cart_owner(client: TestClient, session: Session, add_items_to_cart: tuple[str, Cart, User]):
    token, cart_data, user_dict = add_items_to_cart
    
    new_user = user.create(session, UserCreate(username="testuser2", email="testuser2@example.com", password=SecretStr('Test_1234!')))
    
    data = client.post("/users/login", data={
        "username": "testuser2",
        "password": "Test_1234!"
    })
    
    access_token = data.json()["access_token"]
    
    response = client.put(f"/carts/{user_dict.username}/{cart_data['cart_id']}/update", json={
        "quantity": 3
    }, headers={
        "Authorization": f"Bearer {access_token}"
    })
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Unauthorized to update other user's cart"

def test_update_cart_items_not_enough_stock(client: TestClient, session: Session, add_items_to_cart: tuple[str, Cart, User]):
    token, cart_data, user_dict = add_items_to_cart
    
    response = client.put(f"/carts/{user_dict.username}/{cart_data['cart_id']}/update", json={
        "quantity": 999
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 409
    assert response.json()["detail"] == "Not enough stock"
    
def test_update_cart_items_not_cart_item(client: TestClient, session: Session, add_items_to_cart: tuple[str, Cart, User]):
    token, cart_data, user_dict = add_items_to_cart
    
    response = client.put(f"/carts/{user_dict.username}/999/update", json={
        "quantity": 3
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Cart item not found"

def test_delete_cart_items(client: TestClient, session: Session, add_items_to_cart: tuple[str, Cart, User]):
    token, cart_data, user_dict = add_items_to_cart
    
    response = client.delete(f"/carts/{user_dict.username}/{cart_data['cart_id']}/delete", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 204
    
def test_delete_cart_items_without_token(client: TestClient, session: Session, add_items_to_cart: tuple[str, Cart, User]):
    token, cart_data, user_dict = add_items_to_cart
    
    response = client.delete(f"/carts/{user_dict.username}/{cart_data['cart_id']}/delete")
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    
def test_delete_cart_items_not_user(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict):
    token, user_dict = login_vendor
    
    response = client.delete(f"/carts/{user_dict.username}/1/delete", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 403
    assert response.json()["detail"] == "User is not a customer"
    
def test_delete_cart_items_not_cart_owner(client: TestClient, session: Session, add_items_to_cart: tuple[str, Cart, User]):
    token, cart_data, user_dict = add_items_to_cart
    
    new_user = user.create(session, UserCreate(username="testuser2", email="testuser2@example.com", password=SecretStr("Test_1234!")))
    
    data = client.post("/users/login", data={
        "username": "testuser2",
        "password": "Test_1234!"
    })
    
    access_token = data.json()["access_token"]
    
    response = client.delete(f"/carts/{user_dict.username}/{cart_data['cart_id']}/delete", headers={
        "Authorization": f"Bearer {access_token}"
    })
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Unauthorized to delete other user's cart"

def test_delete_cart_items_not_cart_item(client: TestClient, session: Session, add_items_to_cart: tuple[str, Cart, User]):
    token, cart_data, user_dict = add_items_to_cart
    
    response = client.delete(f"/carts/{user_dict.username}/999/delete", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Cart item not found"

def test_checkout_cart(client: TestClient, session: Session, add_items_to_cart: tuple[str, Cart, User]):
    token, cart_data, user_dict = add_items_to_cart
    
    response = client.get(f"/carts/{user_dict.username}/checkout", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    assert response.json()["total_price"] == "50.00"
    assert response.json()["created_at"] is not None
    assert response.json()["updated_at"] is None

def test_checkout_cart_without_token(client: TestClient, session: Session, add_items_to_cart: tuple[str, Cart, User]):
    token, cart_data, user_dict = add_items_to_cart
    
    response = client.get(f"/carts/{user_dict.username}/checkout")
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    
def test_checkout_cart_not_user(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict):
    token, user_dict = login_vendor
    
    response = client.get(f"/carts/{user_dict.username}/checkout", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 403
    assert response.json()["detail"] == "User is not a customer"
