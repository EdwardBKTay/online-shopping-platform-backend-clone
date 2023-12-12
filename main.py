from fastapi import FastAPI
from sqlmodel import SQLModel
from routes.api import api_router
from db.engine import DB_URL, get_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_db(DB_URL, {"echo": True})
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(api_router)


