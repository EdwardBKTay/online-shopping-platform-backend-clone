from fastapi import APIRouter
from routes.api_user import users_router
from routes.api_vendor import vendor_router

api_router = APIRouter()
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(vendor_router, prefix="/vendors", tags=["Vendors"])
