from fastapi import APIRouter, Depends
from typing import Annotated
from sqlmodel import Session
from utils.deps import get_session

bookmarks_router = APIRouter()

@bookmarks_router.get("/{username}/")
async def get_bookmarks(username: str, session: Annotated[Session, Depends(get_session)]):
    return {"message": "Get all bookmarks for user"}
