# import pytest

# from tests.test_main import client_fixture, session_fixture
# from fastapi.testclient import TestClient
# from tests.crud.test_crud_user import create_test_user
# from pydantic import SecretStr

# class TestGetTokenAPI:
#     def test_api_working(self, client: TestClient, create_test_user: tuple[str, str, SecretStr]):
#         username, email, password = create_test_user
        
#         response = client.post("/token/", data={
#             "username": username,
#             "password": password.get_secret_value()
#         })
        
#         data = response.json()
        
#         assert response.status_code == 200
#         assert "access_token" in data and "token_type" in data
#         assert data["token_type"] == "bearer"
