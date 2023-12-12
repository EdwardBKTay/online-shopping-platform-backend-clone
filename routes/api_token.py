from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from auth.auth import create_access_token, ACCESS_TOKEN_EXPIRATION_MINUTES
from crud.crud_user import user
from core.deps import get_session
from sqlmodel import Session
from typing import Annotated
from schemas.token import TokenPayload, Token
import datetime

token_router = APIRouter()

@token_router.post("/token/")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Annotated[Session, Depends(get_session)]):
    user_obj = user.authenticate(session, form_data.username, form_data.password)
    token_payload = TokenPayload(username=user_obj.username, email=user_obj.email, exp=datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRATION_MINUTES))
    access_token = create_access_token(token_payload)
    return Token(access_token=access_token, token_type="bearer")
