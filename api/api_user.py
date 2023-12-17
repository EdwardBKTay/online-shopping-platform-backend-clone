from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from utils.deps import get_session
from db.models import User
from services.user import user
from schemas.user import UserCreate, UserState
from schemas.token import Token
from typing import Annotated
from auth.auth import ACCESS_TOKEN_EXPIRATION_MINUTES, private_key, create_access_token, verify_password
from fastapi import Response
from jose import jwt
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
    
    user_obj = user.get_username(session, form_data.username)
    is_pwd_valid = verify_password(form_data.password, user_obj.password_hash)
    
    if is_pwd_valid is False:
        raise http_exception
    
    token_payload = UserState(username=user_obj.username, email=user_obj.email, is_vendor=user_obj.is_vendor, is_superuser=user_obj.is_superuser,exp=datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRATION_MINUTES))
    
    access_token = create_access_token(token_payload, private_key)
    
    user_obj.last_signed_in = datetime.datetime.now(datetime.UTC)
    user_obj.auth_token = access_token
    session.add(user_obj)
    session.commit()
    
    return Token(access_token=access_token, token_type="bearer")

@users_router.get("/logout/", dependencies=[Depends(user.get_current_user)])
async def logout_user(response: Response):
    response.headers["Authorization"] = ""
    return {"message": "User logged out successfully"}
