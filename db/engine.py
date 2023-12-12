from sqlmodel import create_engine
from sqlalchemy.exc import DBAPIError
from dotenv import load_dotenv
from typing import Any
from db.models import *
import os

load_dotenv()

DB_URL = f"postgresql+psycopg2://{os.getenv("DB_USERNAME")}:{os.getenv("DB_PASSWORD")}@localhost:5432/{os.getenv("DB_NAME")}"

def get_db(connection_string: str, connection_option: dict[str, Any]):
    if connection_option is None:
        connection_option = {}
    try:
        client = create_engine(connection_string, **connection_option)
        return client
    except DBAPIError as e:
        raise Exception(f"An error occurred: {e}") from e
