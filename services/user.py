from db.models import User
from sqlmodel import Session, select
from fastapi import HTTPException, Depends
from schemas.user import UserCreate
from auth.auth import get_password_hash, verify_password, read_public_key, oauth2_scheme, ALGORITHM
from utils.deps import get_session
from jose import jwt, ExpiredSignatureError, JWTError
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from schemas.user import UserState
from typing import Annotated
import datetime

class CRUDUser:
    def __init__(self, model: User):
        self.model = model
        
    def get_username(self, db: Session, username: str) -> User:
        stmt = select(User).where(User.username == username)
        result = db.exec(stmt).one_or_none()
        
        if result is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        return result
    
    def create(self, db: Session, req_obj: UserCreate) -> User:
        pwd_hash = get_password_hash(req_obj.password.get_secret_value())
        user_obj = self.model(**dict(req_obj), password_hash=pwd_hash, created_at=datetime.datetime.now(datetime.UTC))
        
        try:
            db.add(user_obj)
            db.commit()
            db.refresh(user_obj)
            return user_obj
        
        except IntegrityError as e:
            raise HTTPException(status_code=409, detail="User already exists") from e

    def get_current_user(self, public_key: Annotated[bytes, Depends(read_public_key)], token: Annotated[str, Depends(oauth2_scheme)], session: Annotated[Session, Depends(get_session)]):
        http_exception = HTTPException(status_code=401, detail="Invalid authentication credentials", headers={"WWW-Authenticate": "Bearer"})
        
        try:
            payload = jwt.decode(token, public_key, algorithms=[ALGORITHM], options={"verify_signature": True})
            token_data = UserState.model_validate(payload, strict=True)
            db_obj = self.get_username(session, token_data.username)
            
            if db_obj.auth_token != token:
                raise http_exception

        except ValidationError as e:
            raise http_exception from e
        
        except ExpiredSignatureError as e:
            raise HTTPException(status_code=401, detail="Token has expired", headers={"WWW-Authenticate": "Bearer"}) from e
        
        except JWTError as e:
            raise http_exception from e
        
        return db_obj

user = CRUDUser(User)
