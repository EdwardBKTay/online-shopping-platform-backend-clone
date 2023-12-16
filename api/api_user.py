from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from utils.deps import get_session
from db.models import User
from services.user import user
from schemas.user import UserCreate, UserState
from schemas.token import Token
from typing import Annotated
from auth.auth import ACCESS_TOKEN_EXPIRATION_MINUTES, private_key, create_access_token
import datetime

users_router = APIRouter()

@users_router.get("/")
async def get_user(session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(user.get_current_user)]):
    return user.get_username(session, current_user.username)

@users_router.post("/create/", status_code=201)
async def create_user(session: Annotated[Session, Depends(get_session)], req: UserCreate):
    return user.create(session, req)

@users_router.post("/login/")
async def login_user_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Annotated[Session, Depends(get_session)]):
    http_exception = HTTPException(status_code=401, detail="Invalid user credentials")
    
    user_obj = user.authenticate(session, form_data.username, form_data.password)
    
    if user_obj is None:
        raise http_exception
    
    token_payload = UserState(username=user_obj.username, email=user_obj.email, is_vendor=user_obj.is_vendor, exp=datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRATION_MINUTES))
    
    access_token = create_access_token(token_payload, private_key)
    return Token(access_token=access_token, token_type="bearer")
