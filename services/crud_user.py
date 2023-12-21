from db.models import User
from sqlmodel import Session, select
from fastapi import HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from schemas.user import UserCreate
from auth.auth import get_password_hash, read_public_key, oauth2_scheme
from utils.deps import get_session
from jose import jwt, ExpiredSignatureError, JWTError
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from schemas.user import UserState
from core.config import settings
from typing import Annotated
from datetime import datetime

class CRUDUser:
    def __init__(self, model: User):
        self.model = model
        
    def get_username(self, db: Session, username: str):
        stmt = select(User).where(User.username == username)
        result = db.exec(stmt).one_or_none()
        
        if result is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        return result
    
    def create(self, db: Session, req_obj: UserCreate) -> User:
        pwd_hash = get_password_hash(req_obj.password.get_secret_value())
        user_obj = User(**jsonable_encoder(req_obj), password_hash=pwd_hash, created_at=datetime.now())
        
        try:
            db.add(user_obj)
            db.commit()
            db.refresh(user_obj)
            return user_obj
        
        except IntegrityError as e:
            raise HTTPException(status_code=409, detail="User already exists") from e

user = CRUDUser(User)

def get_current_user(public_key: Annotated[bytes, Depends(read_public_key)], token: Annotated[str, Depends(oauth2_scheme)], session: Annotated[Session, Depends(get_session)]) -> User:
        http_exception = HTTPException(status_code=401, detail="Invalid authentication credentials", headers={"WWW-Authenticate": "Bearer"})
        
        try:
            payload = jwt.decode(token, public_key, algorithms=[settings.ACCESS_TOKEN_ALGORITHM], options={"verify_signature": True})
            token_data = UserState.model_validate(payload, strict=True)
            db_obj = user.get_username(session, token_data.username)
            if db_obj.auth_token != token:
                raise http_exception
        except ValidationError as e:
            raise http_exception from e
        except ExpiredSignatureError as e:
            raise HTTPException(status_code=401, detail="Token has expired", headers={"WWW-Authenticate": "Bearer"}) from e
        except JWTError as e:
            raise http_exception from e
        
        return db_obj

def is_only_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.is_vendor is True or current_user.is_superuser is True:
        raise HTTPException(status_code=403, detail="User is not a customer")
    
    return current_user

def is_user_vendor(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.is_vendor is False:
        raise HTTPException(status_code=403, detail="User is not a vendor")
    
    return current_user

def is_user_superuser(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.is_superuser is False:
        raise HTTPException(status_code=403, detail="User is not a superuser")
    
    return current_user
