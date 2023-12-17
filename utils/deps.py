from db.engine import get_db, DB_URL
from sqlmodel import Session

def get_session():
    engine = get_db(DB_URL, {"echo": True})
    with Session(engine) as session:
        yield session

