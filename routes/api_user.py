from typing import Annotated
from fastapi import APIRouter, Form, Depends, HTTPException, status
from pydantic import EmailStr, SecretStr, ValidationError
from sqlmodel import Session
from db.models import User

from schemas.user import UserCreate
from crud.crud_user import user
from core.deps import get_session, get_current_entity

users_router = APIRouter()

# TODO: route for profile of users (GET)
@users_router.get("/", dependencies=[Depends(get_current_entity)])
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
