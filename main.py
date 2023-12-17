from fastapi import FastAPI, APIRouter
from sqlmodel import SQLModel
from db.engine import DB_URL, get_db
from contextlib import asynccontextmanager
from api.api_user import users_router
from api.api_product import products_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_db(DB_URL, {"echo": True})
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

api_router = APIRouter()
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(products_router, prefix="/products", tags=["Products"])
# api_router.include_router(vendor_router, prefix="/vendors", tags=["Vendors"])

app.include_router(api_router)


