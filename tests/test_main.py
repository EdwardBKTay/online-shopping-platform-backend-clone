import pytest

from sqlmodel import SQLModel
from core.deps import get_session
from main import app
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session
from sqlmodel.pool import StaticPool
from db.models import User
import os

@pytest.fixture(name="session", scope="function")
def session_fixture():
    TEST_DB_URL = f"postgresql+psycopg2://{os.getenv("DB_USERNAME")}:{os.getenv("DB_PASSWORD")}@localhost:5432/{os.getenv("TEST_DB_NAME")}"
    
    engine = create_engine(TEST_DB_URL, poolclass=StaticPool)
    connection = engine.connect()
    transaction = connection.begin()
    
    SQLModel.metadata.create_all(bind=engine)
    session = Session(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()
    
    engine.dispose()

@pytest.fixture(name="client", scope="function")
def client_fixture(session: Session):
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
