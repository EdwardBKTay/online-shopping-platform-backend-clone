import datetime
import secrets

from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from jose import ExpiredSignatureError, JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from auth.auth import get_password_hash, oauth2_scheme, read_public_key
from core.config import settings
from db.models import EmailVerification, User
from schemas.token import EmailVerificationToken
from schemas.user import UserCreate, UserState
from utils.deps import get_session


class CRUDUser:
    def __init__(self, model: User):
        self.model = model
        
    def get_username(self, db: Session, username: str):
        stmt = select(User).where(User.username == username)
        result = db.exec(stmt).one_or_none()
        
        if result is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        return result
    
    def get_email(self, db: Session, email: str):
        stmt = select(User).where(User.email == email)
        result = db.exec(stmt).one_or_none()
        
        if result is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        return result
    
    def create(self, db: Session, req_obj: UserCreate):
        pwd_hash = get_password_hash(req_obj.password.get_secret_value())
        user_obj = User(**jsonable_encoder(req_obj), password_hash=pwd_hash, created_at=datetime.datetime.now())
        
        try:
            db.add(user_obj)
            db.commit()
            db.refresh(user_obj)
            return user_obj
        
        except IntegrityError as e:
            raise HTTPException(status_code=409, detail="User already exists") from e
        
    def create_email_verification_token(self, db: Session, email: str, expiration_seconds: int | None = None) -> EmailVerificationToken:
        token = secrets.token_urlsafe(32)
        
        if expiration_seconds is None:
            expiration_time = datetime.datetime.now() + datetime.timedelta(seconds=settings.EMAIL_VERIFICATION_TOKEN_EXPIRATION_SECONDS)
        else:
            expiration_time = datetime.datetime.now() + datetime.timedelta(seconds=expiration_seconds)
        
        db_obj = EmailVerification(email=email, token=token, expires_at=expiration_time)
        
        db.add(db_obj)
        db.commit()
        
        return EmailVerificationToken(email_verification_token=token)

user = CRUDUser(User)

def get_current_user(public_key: Annotated[bytes, Depends(read_public_key)], token: Annotated[str, Depends(oauth2_scheme)], session: Annotated[Session, Depends(get_session)]) -> User:
        http_exception = HTTPException(status_code=401, detail="Invalid authentication credentials", headers={"WWW-Authenticate": "Bearer"})
        
        try:
            payload = jwt.decode(token, public_key, algorithms=[settings.ACCESS_TOKEN_ALGORITHM], options={"verify_signature": True})
            token_data = UserState.model_validate(payload, strict=True)
            db_obj = user.get_username(session, token_data.username)
            if db_obj.auth_token != token:
                raise http_exception
            # if db_obj.is_email_verified is False:
            #     raise HTTPException(status_code=401, detail="Email is not verified", headers={"WWW-Authenticate": "Bearer"}) # ! uncomment this line in production
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
