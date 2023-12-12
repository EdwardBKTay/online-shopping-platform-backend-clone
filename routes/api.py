from fastapi import APIRouter
from routes.api_user import users_router
from routes.api_token import token_router

api_router = APIRouter()
api_router.include_router(token_router, tags=["Token"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])

