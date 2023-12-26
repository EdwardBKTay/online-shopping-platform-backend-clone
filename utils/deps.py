from sqlmodel import Session

from db.engine import DB_URL, get_db


def get_session():
    engine = get_db(DB_URL, {"echo": True})
    with Session(engine) as session:
        yield session

