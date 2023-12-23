import pytest

from tests.test_main import client_fixture, session_fixture
from fastapi.testclient import TestClient
from sqlmodel import Session

def test_get_orders(client: TestClient, session: Session):
    response = client.get("/orders/testuser/")
    assert response.status_code == 200
    assert response.json() == []
