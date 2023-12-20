from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from utils.deps import get_session
from db.models import User
from services.crud_user import user, get_current_user
from schemas.user import UserCreate, UserState
from schemas.token import Token
from typing import Annotated
from auth.auth import ACCESS_TOKEN_EXPIRATION_MINUTES, private_key, create_access_token, verify_password
from fastapi import Response
import datetime

users_router = APIRouter()

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

@users_router.get("/logout/")
async def logout_user(response: Response, current_user: Annotated[User, Depends(get_current_user)], session: Annotated[Session, Depends(get_session)]):
    user_obj = user.get_username(session, current_user.username)
    user_obj.auth_token = ""
    session.add(user_obj)
    session.commit()
    
    response.headers["Authorization"] = ""
    
    return {"message": "User logged out successfully"}

@users_router.get("/{username}/")
async def get_user(username: str, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.username != username:
        raise HTTPException(status_code=403, detail="Not allowed to access other user's data")
    return user.get_username(session, current_user.username)
