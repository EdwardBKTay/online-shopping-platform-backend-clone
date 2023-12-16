import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from auth.auth import ACCESS_TOKEN_EXPIRATION_MINUTES, create_access_token
from crud.crud_vendor import vendor

from core.deps import get_current_entity, get_session
from schemas.token import TokenPayload, Token
from schemas.vendor import VendorCreate
from pydantic import EmailStr, SecretStr, ValidationError

vendor_router = APIRouter()

@vendor_router.get("/{vendor_username}", dependencies=[Depends(get_current_entity)])
async def get_vendor(vendor_username: str, session: Annotated[Session, Depends(get_session)]):
    return vendor.get(session, vendor_username)

@vendor_router.post("/create/", status_code=201)
async def create_vendor(username: Annotated[str, Form()], email: Annotated[EmailStr, Form()], password: Annotated[SecretStr, Form()], session: Annotated[Session, Depends(get_session)]):
    try:
        vendor_in = VendorCreate(username=username, email=email, password=password)
        print(vendor_in)
        vendor.create(session, vendor_in)
        return {"message": "Vendor has been created"}
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Validation Error: {e}") from e

@vendor_router.post("/token/")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Annotated[Session, Depends(get_session)]):
    http_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid vendor credentials")
    
    vendor_obj = vendor.authenticate(session, form_data.username, form_data.password)
    
    if vendor_obj is None:
        raise http_exception

    token_payload = TokenPayload(username=vendor_obj.username, email=vendor_obj.email, exp=datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRATION_MINUTES))

    access_token = create_access_token(token_payload)
    return Token(access_token=access_token, token_type="bearer")
