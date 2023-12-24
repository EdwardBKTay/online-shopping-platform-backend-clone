# https://stackoverflow.blog/2020/03/02/best-practices-for-rest-api-design/

# Case study on StackOverflow: https://www.linkedin.com/pulse/case-study-how-stackoverflows-monolith-beats-navjot-bansal

from fastapi import FastAPI, APIRouter
from sqlmodel import SQLModel, Session
from db.engine import DB_URL, get_db
from contextlib import asynccontextmanager
from api.api_user import users_router
from api.api_product import products_router
from api.api_cart import carts_router
from api.api_order import orders_router
from api.api_bookmark import bookmarks_router
from fastapi.middleware.cors import CORSMiddleware
from utils.utils import set_default_product_categories

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_db(DB_URL, {"echo": True})
    # SQLModel.metadata.drop_all(engine) # remove this line when deploying to production
    SQLModel.metadata.create_all(engine)
    # set_default_product_categories(Session(engine)) # remove this line when deploying to production
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# TODO: create a middleware to get the Authorization header from the request and verify the token if there is one and store the current_user in app.state so that it can be accessed in the routers. If there is no token, then the current_user will be None

api_router = APIRouter()
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(products_router, prefix="/products", tags=["Products"])
api_router.include_router(carts_router, prefix="/carts", tags=["Carts"])
api_router.include_router(orders_router, prefix="/orders", tags=["Orders"])
api_router.include_router(bookmarks_router, prefix="/bookmarks", tags=["Bookmarks"])

app.include_router(api_router)




