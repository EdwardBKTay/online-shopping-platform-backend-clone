# import pytest

# from tests.test_main import client_fixture, session_fixture
# from fastapi.testclient import TestClient
# from schemas.user import UserCreate
# from sqlmodel import Session
# from services.crud_user import user
# from db.models import User, Cart
# from schemas.cart import CartCreate, CartUpdate
# from pydantic import SecretStr
# from tests.api.test_api_product import create_product, login_vendor
# from tests.api.test_api_user import login_user

# def test_add_to_cart(client: TestClient, session: Session, login_user: tuple[str, User], create_product: dict):
#     token, user_dict = login_user
    
#     response = client.post("/carts/add/", json={
#         "product_id": create_product["id"],
#         "quantity": 5
#     }, headers={
#         "Authorization": f"Bearer {token}"
#     })
    
#     assert response.status_code == 201
#     assert response.json()["product_id"] == create_product["id"]
#     assert response.json()["quantity"] == 5
#     assert response.json()["user_id"] == user_dict.id
#     assert "created_at" in response.json() and response.json()["created_at"] is not None
#     assert "updated_at" in response.json() and response.json()["updated_at"] is None

# def test_add_to_cart_without_token(client: TestClient, session: Session, create_product: dict):
#     response = client.post("/carts/add/", json={
#         "product_id": create_product["id"],
#         "quantity": 5
#     })
    
#     assert response.status_code == 401
#     assert response.json()["detail"] == "Not authenticated"
    
# def test_add_to_cart_not_user(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict):
#     token, user_dict = login_vendor
    
#     response = client.post("/carts/add/", json={
#         "product_id": create_product["id"],
#         "quantity": 5
#     }, headers={
#         "Authorization": f"Bearer {token}"
#     })
    
#     assert response.status_code == 403
#     assert response.json()["detail"] == "User is not a customer"

# def test_add_to_cart_invalid_product(client: TestClient, session: Session, login_user: tuple[str, User]):
#     token, user_dict = login_user
    
#     response = client.post("/carts/add/", json={
#         "product_id": 999,
#         "quantity": 5
#     }, headers={
#         "Authorization": f"Bearer {token}"
#     })
    
#     assert response.status_code == 404
#     assert response.json()["detail"] == "Product not found"
    
# def test_add_to_cart_not_enough_stock(client: TestClient, session: Session, login_user: tuple[str, User], create_product: dict):
#     token, user_dict = login_user
    
#     response = client.post("/carts/add/", json={
#         "product_id": create_product["id"],
#         "quantity": 999
#     }, headers={
#         "Authorization": f"Bearer {token}"
#     })
    
#     assert response.status_code == 409
#     assert response.json()["detail"] == "Not enough stock"

# def test_add_to_cart_duplicated_product(client: TestClient, session: Session, login_user: tuple[str, User], create_product: dict):
#     token, user_dict = login_user
    
#     client.post("/carts/add/", json={
#         "product_id": create_product["id"],
#         "quantity": 5
#     }, headers={
#         "Authorization": f"Bearer {token}"
#     })
    
#     response = client.post("/carts/add/", json={
#         "product_id": create_product["id"],
#         "quantity": 5
#     }, headers={
#         "Authorization": f"Bearer {token}"
#     })
    
#     assert response.status_code == 409
#     assert response.json()["detail"] == "Product already in cart"
    
# def test_get_user_cart(client: TestClient, session: Session, login_user: tuple[str, User], create_product: dict):
#     token, user_dict = login_user
    
#     client.post("/carts/add/", json={
#         "product_id": create_product["id"],
#         "quantity": 5
#     }, headers={
#         "Authorization": f"Bearer {token}"
#     })
    
#     response = client.get(f"/carts/", headers={
#         "Authorization": f"Bearer {token}"
#     })
    
#     assert response.status_code == 200
#     assert len(response.json()) == 1
#     assert response.json()[0]["product_id"] == create_product["id"]
#     assert response.json()[0]["quantity"] == 5
#     assert response.json()[0]["user_id"] == user_dict.id
#     assert "created_at" in response.json()[0] and response.json()[0]["created_at"] is not None
#     assert "updated_at" in response.json()[0] and response.json()[0]["updated_at"] is None
    
# def test_get_user_cart_without_token(client: TestClient, session: Session, login_user: tuple[str, User], create_product: dict):
    
#     response = client.get(f"/carts/")
    
#     assert response.status_code == 401
#     assert response.json()["detail"] == "Not authenticated"

# # def test_get_user_cart_not_user(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict):

# def test_get_user_cart_not_user(client: TestClient, session: Session, login_vendor: tuple[str, User], create_product: dict):
#     token, user_dict = login_vendor
    
#     response = client.get(f"/carts/", headers={
#         "Authorization": f"Bearer {token}"
#     })
    
#     assert response.status_code == 403
#     assert response.json()["detail"] == "User is not a customer"
    
# @pytest.fixture
# def create_cart(client: TestClient, session: Session, login_user: tuple[str, User], create_product: dict) -> tuple[str, Cart, User]:
#     token, user_dict = login_user
    
#     cart_data = client.post("/carts/add/", json={
#         "product_id": create_product["id"],
#         "quantity": 5
#     }, headers={
#         "Authorization": f"Bearer {token}"
#     }).json()
    
#     return token, cart_data, user_dict
    
# def test_update_cart_items(client: TestClient, session: Session, create_cart: tuple[str, Cart, User]):
#     token, cart_data, user_dict = create_cart
    
#     response = client.put(f"/carts/{cart_data['id']}/update", json={
#         "quantity": 3
#     }, headers={
#         "Authorization": f"Bearer {token}"
#     })
    
#     assert response.status_code == 200
#     assert response.json()["product_id"] == cart_data["id"]
#     assert response.json()["quantity"] == 3
#     assert response.json()["user_id"] == user_dict.id
#     assert "created_at" in response.json() and response.json()["created_at"] is not None
#     assert "updated_at" in response.json() and response.json()["updated_at"] is not None
    
# def test_update_cart_items_without_token(client: TestClient, session: Session, create_cart: tuple[str, Cart, User]):
#     token, cart_data, user_dict = create_cart
    
#     response = client.put(f"/carts/{cart_data['id']}/update", json={
#         "quantity": 3
#     })
    
#     assert response.status_code == 401
#     assert response.json()["detail"] == "Not authenticated"
    
# def test_update_cart_items_not_user(client: TestClient, session: Session, create_cart: tuple[str, Cart, User], login_vendor: tuple[str, User]):
#     token, cart_data, user_dict = create_cart
    
#     response = client.put(f"/carts/{cart_data['id']}/update", json={
#         "quantity": 3
#     }, headers={
#         "Authorization": f"Bearer {login_vendor[0]}"
#     })
    
#     assert response.status_code == 403
#     assert response.json()["detail"] == "User is not a customer"
    
# def test_update_cart_items_not_cart_owner(client: TestClient, session: Session, create_cart: tuple[str, Cart, User]):
#     token, cart_data, user_dict = create_cart
    
#     new_user = user.create(session, UserCreate(username="testuser2", email="testuser2@example.com", password=SecretStr("Test_1234!")))
    
#     data = client.post("/users/login", data={
#         "username": "testuser2",
#         "password": "Test_1234!"
#     })
    
#     access_token = data.json()["access_token"]
    
#     response = client.put(f"/carts/{cart_data['id']}/update", json={
#         "quantity": 3
#     }, headers={
#         "Authorization": f"Bearer {access_token}"
#     })
    
#     assert response.status_code == 403
#     assert response.json()["detail"] == "Unauthorized to update cart"
    
# def test_update_cart_items_not_enough_stock(client: TestClient, session: Session, create_cart: tuple[str, Cart, User], create_product: dict):
#     token, cart_data, user_dict = create_cart
    
#     response = client.put(f"/carts/{cart_data['id']}/update", json={
#         "quantity": 999
#     }, headers={
#         "Authorization": f"Bearer {token}"
#     })
    
#     assert response.status_code == 409
#     assert response.json()["detail"] == "Not enough stock"
    
# def test_delete_cart_items(client: TestClient, session: Session, create_cart: tuple[str, Cart, User]):
#     token, cart_data, user_dict = create_cart
    
#     response = client.delete(f"/carts/{cart_data['id']}/delete", headers={
#         "Authorization": f"Bearer {token}"
#     })
    
#     assert response.status_code == 204
    
# def test_delete_cart_items_without_token(client: TestClient, session: Session, create_cart: tuple[str, Cart, User]):
#     token, cart_data, user_dict = create_cart
    
#     response = client.delete(f"/carts/{cart_data['id']}/delete")
    
#     assert response.status_code == 401
#     assert response.json()["detail"] == "Not authenticated"
    
# def test_delete_cart_items_not_user(client: TestClient, session: Session, create_cart: tuple[str, Cart, User], login_vendor: tuple[str, User]):
#     token, cart_data, user_dict = create_cart
    
#     response = client.delete(f"/carts/{cart_data['id']}/delete", headers={
#         "Authorization": f"Bearer {login_vendor[0]}"
#     })
    
#     assert response.status_code == 403
#     assert response.json()["detail"] == "User is not a customer"
    
# def test_delete_cart_items_not_cart_owner(client: TestClient, session: Session, create_cart: tuple[str, Cart, User]):
#     token, cart_data, user_dict = create_cart
    
#     new_user = user.create(session, UserCreate(username="testuser2", email="testuser2@example.com", password=SecretStr("Test_1234!"))) 
    
#     data = client.post("/users/login", data={
#         "username": "testuser2",
#         "password": "Test_1234!"
#     })
    
#     access_token = data.json()["access_token"]
    
#     response = client.delete(f"/carts/{cart_data['id']}/delete", headers={
#         "Authorization": f"Bearer {access_token}"
#     })
    
#     assert response.status_code == 403
#     assert response.json()["detail"] == "Unauthorized to delete cart"
