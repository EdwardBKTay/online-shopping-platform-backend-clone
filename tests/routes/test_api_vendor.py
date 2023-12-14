import pytest

from tests.test_main import client_fixture, session_fixture
from fastapi.testclient import TestClient

class TestGetVendorByUsernameAPI:
    def setup_vendor(self, client: TestClient):
        client.post("/vendors/create/", data={
            "vendor_username": "testvendor",
            "vendor_email": "testvendor@example.com",
            "vendor_password": "Test&@1234!"
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        
        client.post("/token/", data={
            "username": "testvendor",
            "password": "Test&@1234!"
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        
    def test_api_working(self, client: TestClient):
        self.setup_vendor(client)
        
        response = client.get("/vendors/testvendor/")
        
        data = response.json()
        
        assert response.status_code == 200
        assert data["username"] == "testvendor"
        assert data["email"] == "testvendor@example.com"
        assert data["id"] is not None
    
    def test_bad_vendor_username(self, client: TestClient):
        self.setup_vendor(client)
        
        response = client.get("/vendors/test/")
        
        data = response.json()
        
        assert response.status_code == 404
        assert "detail" in data and data["detail"] == "Not found"
        
class TestVendorCreationAPI:
    def test_api_working(self, client: TestClient):
        response = client.post("/vendors/create/", data={
            "vendor_username": "testvendor",
            "vendor_email": "testvendor@example.com",
            "vendor_password": "Test&@1234!"
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        
        response_data = response.json()
        
        assert response.status_code == 201
        assert "message" in response_data and response_data["message"] == "Vendor has been created"
        
    def test_bad_vendor_username(self, client: TestClient):
        response = client.post("/vendors/create/", data={
            "vendor_username": "test vendor",
            "vendor_email": "testvendor@example.com",
            "vendor_password": "Test_12345!"
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        
        assert response.status_code == 400
        assert "Validation Error" in response.json()["detail"]
        
    def test_bad_vendor_email(self, client: TestClient):
        response = client.post("/vendors/create/", data={
            "vendor_username": "testvendor",
            "vendor_email": "testvendor@example",
            "vendor_password": "Test_12345!"
        }, headers={
            "Content-Type": "application/x-www-form-urlencoded"
        })
        
        assert response.status_code == 422
        
    def test_bad_vendor_password(self, client: TestClient):
        response = client.post("/vendors/create/", data={
            "vendor_username": "testvendor",
            "vendor_email": "testvendor@example.com",
            "vendor_password": "test"
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        
        assert response.status_code == 400
