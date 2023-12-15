from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlmodel import Session
from crud.crud_vendor import vendor

from core.deps import get_current_entity, get_session
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
