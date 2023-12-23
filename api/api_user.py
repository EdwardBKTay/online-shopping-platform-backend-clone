# Reference for SQL injection attack: https://www.w3schools.com/sql/sql_injection.asp

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from sqlmodel import Session, select
from utils.deps import get_session
from db.models import User, UserRead, UserReadAll
from services.crud_user import user, get_current_user
from schemas.user import UserCreate, UserState, ForgotPassword
from schemas.token import Token, RefreshToken
from typing import Annotated
from auth.auth import read_private_key, create_access_token, verify_password, create_refresh_token
from jose import jwt, JWTError, ExpiredSignatureError
from core.config import settings
import datetime
import secrets

users_router = APIRouter()

@users_router.post("/create/", status_code=201, response_model=UserRead)
async def create_user(session: Annotated[Session, Depends(get_session)], req: UserCreate):
    return user.create(session, req)

@users_router.post("/login/", response_model=Token)
async def login_for_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Annotated[Session, Depends(get_session)]):
    http_exception = HTTPException(status_code=401, detail="Invalid user credentials")
    
    user_obj = user.get_username(session, form_data.username)
    is_pwd_valid = verify_password(form_data.password, user_obj.password_hash)
    
    if is_pwd_valid is False:
        raise http_exception
    
    access_token_payload = UserState(username=user_obj.username, email=user_obj.email, is_vendor=user_obj.is_vendor, is_superuser=user_obj.is_superuser,exp=datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=settings.ACCESS_TOKEN_EXPIRATION_SECONDS))
    
    refresh_token_payload = UserState(username=user_obj.username, email=user_obj.email, is_vendor=user_obj.is_vendor, is_superuser=user_obj.is_superuser,exp=datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(seconds=settings.REFRESH_TOKEN_EXPIRATION_SECONDS))
    
    access_token = create_access_token(access_token_payload, read_private_key())
    refresh_token = create_refresh_token(refresh_token_payload, settings.REFRESH_TOKEN_SECRET_KEY)
    
    user_obj.last_signed_in = datetime.datetime.now(datetime.UTC)
    user_obj.auth_token = access_token
    user_obj.refresh_token = refresh_token
    session.add(user_obj)
    session.commit()
    
    return Token(access_token=access_token, token_type="bearer", refresh_token=refresh_token)

@users_router.get("/logout/")
async def logout_user(current_user: Annotated[User, Depends(get_current_user)], session: Annotated[Session, Depends(get_session)]):
    user_obj = user.get_username(session, current_user.username)
    user_obj.auth_token = ""
    user_obj.refresh_token = ""
    session.add(user_obj)
    session.commit()
    
    return {"message": "User logged out successfully"}

@users_router.get("/{username}/", response_model=UserReadAll)
async def get_user(username: str, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.username != username:
        raise HTTPException(status_code=403, detail="Not allowed to access other user's data")
    return user.get_username(session, current_user.username)

@users_router.post("/token/refresh/", response_model=Token)
async def refresh_access_token(req: RefreshToken, session: Annotated[Session, Depends(get_session)]):
    try:
        decoded_token = jwt.decode(req.refresh_token, settings.REFRESH_TOKEN_SECRET_KEY, algorithms=[settings.REFRESH_TOKEN_ALGORITHM])
        decoded_token = UserState.model_validate(decoded_token)
    except ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail="Refresh token expired") from e
    except ValidationError or JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token") from e

    db_user = user.get_username(session, decoded_token.username)
    
    if db_user.refresh_token != req.refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    new_access_token_payload = UserState(username=db_user.username, email=db_user.email, is_vendor=db_user.is_vendor, is_superuser=db_user.is_superuser,exp=datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=settings.ACCESS_TOKEN_EXPIRATION_SECONDS))
    
    new_refresh_token_payload = UserState(username=db_user.username, email=db_user.email, is_vendor=db_user.is_vendor, is_superuser=db_user.is_superuser,exp=datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=settings.REFRESH_TOKEN_EXPIRATION_SECONDS))
    
    new_access_token = create_access_token(new_access_token_payload, read_private_key())
    new_refresh_token = create_refresh_token(new_refresh_token_payload, settings.REFRESH_TOKEN_SECRET_KEY)
    
    db_user.auth_token = new_access_token
    db_user.refresh_token = new_refresh_token
    session.add(db_user)
    session.commit()
    
    return Token(access_token=new_access_token, token_type="bearer", refresh_token=new_refresh_token)
