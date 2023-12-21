from sqlmodel import create_engine
from sqlalchemy.exc import DBAPIError
from typing import Any
from db.models import *
from core.config import settings

DB_URL = f"postgresql+psycopg2://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@localhost:5432/{settings.DB_NAME}"

def get_db(connection_string: str, connection_option: dict[str, Any]):
    if connection_option is None:
        connection_option = {}
    try:
        client = create_engine(connection_string, **connection_option)
        return client
    except DBAPIError as e:
        raise Exception(f"An error occurred: {e}") from e
