from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from typing import Annotated
from core.deps import get_session
from db.models import User
from user.crud import user
from user.schema import UserCreate
from utils.token_schema import TokenPayload, Token
from auth.auth import ACCESS_TOKEN_EXPIRATION_MINUTES, create_access_token, private_key
import datetime


users_router = APIRouter()

@users_router.get("/me/")
async def get_user(session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(user.get_current_user)]):
    db_obj = user.get_username(session, current_user.username)
    
    if db_obj is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return db_obj

@users_router.post("/create/", status_code=201)
async def create_user(session: Annotated[Session, Depends(get_session)], req: UserCreate):
    return user.create(session, req)

@users_router.post("/token/")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Annotated[Session, Depends(get_session)]):
    http_exception = HTTPException(status_code=401, detail="Invalid user credentials")
    
    user_obj = user.authenticate(session, form_data.username, form_data.password)
    
    if user_obj is None:
        raise http_exception
    
    token_payload = TokenPayload(username=user_obj.username, email=user_obj.email, exp=datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRATION_MINUTES))
    
    access_token = create_access_token(token_payload, private_key)
    
    return Token(access_token=access_token, token_type="bearer")
