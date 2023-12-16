from typing import Generic, TypeVar, Any, Union, Annotated
from sqlmodel import Session, select
from fastapi import HTTPException, Depends
from auth.auth import get_password_hash, verify_password, user_oauth2_scheme, ALGORITHM, read_public_key
from utils.token_schema import TokenPayload
from core.deps import get_session
from jose import jwt, ExpiredSignatureError, JWTError
from pydantic import ValidationError
from pydantic import BaseModel, SecretStr
from sqlalchemy.exc import IntegrityError
import datetime

class CreateSchemaBaseModel(BaseModel):
    username: str
    email: str
    password: SecretStr

DBModelType = TypeVar("DBModelType", bound=Any)
CreateSchemaType = TypeVar("CreateSchemaType", bound=CreateSchemaBaseModel)

class CRUDBase(Generic[DBModelType, CreateSchemaType]):
    def __init__(self, model: DBModelType):
        self.model = model
        
    def get_username(self, db: Session, username: str) -> Union[DBModelType, None]:
        stmt = select(self.model).where(self.model.username == username)
        result = db.exec(stmt).one_or_none()
        return result

    def create(self, db: Session, req_obj: CreateSchemaType) -> DBModelType:
        pwd_hash = get_password_hash(req_obj.password.get_secret_value())
        user_obj = self.model(**dict(req_obj), password_hash=pwd_hash, created_at=datetime.datetime.now(datetime.UTC))
        try:
            db.add(user_obj)
            db.commit()
            db.refresh(user_obj)
            return user_obj
        
        except IntegrityError as e:
            raise HTTPException(status_code=409, detail="User already exists") from e

    def authenticate(self, db: Session, username: str, password: str) -> Union[DBModelType, None]:
        user_obj = self.get_username(db, username)
        if user_obj is None:
            return None
        is_pwd_valid = verify_password(password, user_obj.password_hash)
        if is_pwd_valid:
            user_obj.last_signed_in = datetime.datetime.now(datetime.UTC)
            db.add(user_obj)
            db.commit()
            db.refresh(user_obj)
            return user_obj
        return None


