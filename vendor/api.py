from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from typing import Annotated
from core.deps import get_session
from db.models import Vendor
from vendor.crud import vendor
from vendor.schema import VendorCreate
from utils.token_schema import TokenPayload, Token
from auth.auth import ACCESS_TOKEN_EXPIRATION_MINUTES, create_access_token, private_key
import datetime

vendor_router = APIRouter()

@vendor_router.get("/me/")
async def get_user(session: Annotated[Session, Depends(get_session)], current_user: Annotated[Vendor, Depends(vendor.get_current_vendor)]):
    db_obj = vendor.get_username(session, current_user.username)
    
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    return db_obj

@vendor_router.post("/create/", status_code=201)
async def create_user(session: Annotated[Session, Depends(get_session)], req: VendorCreate):
    return vendor.create(session, req)

@vendor_router.post("/token/")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Annotated[Session, Depends(get_session)]):
    http_exception = HTTPException(status_code=401, detail="Invalid user credentials")
    
    user_obj = vendor.authenticate(session, form_data.username, form_data.password)
    
    if user_obj is None:
        raise http_exception
    
    token_payload = TokenPayload(username=user_obj.username, email=user_obj.email, exp=datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRATION_MINUTES))
    
    access_token = create_access_token(token_payload, private_key)
    
    return Token(access_token=access_token, token_type="bearer")
