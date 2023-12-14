from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlmodel import Session
from core.deps import get_current_user, get_session
from crud.crud_vendor import vendor
from typing import Annotated
from pydantic import EmailStr, SecretStr, ValidationError

from schemas.vendor import VendorCreate


vendor_router = APIRouter()

@vendor_router.get("/{vendor_username}", dependencies=[Depends(get_current_user)])
async def get_vendor(vendor_username: str, session: Annotated[Session, Depends(get_session)]):
    return vendor.get(session, vendor_username)

@vendor_router.post("/create/", status_code=201)
async def create_vendor(vendor_username: Annotated[str, Form()], vendor_email: Annotated[EmailStr, Form()], vendor_password: Annotated[SecretStr, Form()], session: Annotated[Session, Depends(get_session)]):
    try:
        vendor_in = VendorCreate(username=vendor_username, email=vendor_email, password=vendor_password)
        vendor.create(session, vendor_in)
        return {"message": "Vendor has been created"}
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Validation Error: {e}") from e
