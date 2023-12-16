import datetime
from typing import Annotated
from fastapi import APIRouter, Form, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr, SecretStr, ValidationError
from sqlmodel import Session
from auth.auth import ACCESS_TOKEN_EXPIRATION_MINUTES, create_access_token
from db.models import User
from schemas.token import TokenPayload, Token

from schemas.user import UserCreate
from crud.crud_user import user
from core.deps import get_session, get_current_entity

users_router = APIRouter()

# TODO: route for profile of users (GET)
@users_router.get("/me")
async def get_user(session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_entity)]):
    return user.get(session, current_user.username)

@users_router.post("/create/", status_code=201)
async def create_user(username: Annotated[str, Form()], email: Annotated[EmailStr, Form()], password: Annotated[SecretStr, Form()], session: Annotated[Session, Depends(get_session)]):
    try:
        user_in = UserCreate(username=username, email=email, password=password)
        user.create(session, user_in)
        return {"message": "User has been created"}
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Validation Error: {e}") from e

@users_router.post("/token/")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Annotated[Session, Depends(get_session)]):
    http_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user credentials")
    
    user_obj = user.authenticate(session, form_data.username, form_data.password)
    
    if user_obj is None:
        raise http_exception

    token_payload = TokenPayload(username=user_obj.username, email=user_obj.email, exp=datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRATION_MINUTES))

    access_token = create_access_token(token_payload)
    return Token(access_token=access_token, token_type="bearer")
