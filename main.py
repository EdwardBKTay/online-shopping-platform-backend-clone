# Reference to rest api design: https://stackoverflow.blog/2020/03/02/best-practices-for-rest-api-design/

# Case study on StackOverflow: https://www.linkedin.com/pulse/case-study-how-stackoverflows-monolith-beats-navjot-bansal

import time

from contextlib import asynccontextmanager

import uvicorn

from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, SQLModel

from api.api_cart import carts_router
from api.api_files import files_router
from api.api_order import orders_router
from api.api_product import products_router
from api.api_user import users_router
from db.engine import DB_URL, get_db
from utils.utils import set_default_product_categories


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_db(DB_URL, {"echo": True})
    SQLModel.metadata.drop_all(engine) # ! remove this line when deploying to production
    SQLModel.metadata.create_all(engine)
    set_default_product_categories(Session(engine)) # ! remove this line when deploying to production
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

api_router = APIRouter()
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(products_router, prefix="/products", tags=["Products"])
api_router.include_router(carts_router, prefix="/carts", tags=["Carts"])
api_router.include_router(orders_router, prefix="/orders", tags=["Orders"])
api_router.include_router(files_router, prefix="/files", tags=["Files"])

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app", log_level="info", reload=True)



