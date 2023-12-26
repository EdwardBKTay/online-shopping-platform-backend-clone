import pytest

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from core.config import settings
from db.models import *
from main import app
from utils.deps import get_session
from utils.utils import set_default_product_categories


@pytest.fixture(name="session")
def session_fixture():
    TEST_DB_URL = f"postgresql+psycopg2://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@localhost:5432/{settings.TEST_DB_NAME}"
    
    engine = create_engine(TEST_DB_URL, poolclass=StaticPool)
    connection = engine.connect()
    
    SQLModel.metadata.create_all(bind=engine)
    session = Session(bind=connection)
    set_default_product_categories(session)
    
    yield session
    
    session.close()
    
    SQLModel.metadata.drop_all(bind=engine)
    
    engine.dispose()

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
