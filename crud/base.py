from typing import Generic, TypeVar, Any
from sqlmodel import Session, select
from fastapi import HTTPException, status
from sqlalchemy.exc import NoResultFound, IntegrityError
from auth.auth import get_password_hash, verify_password
from pydantic import BaseModel, SecretStr
import datetime

DBModelType = TypeVar("DBModelType", bound=Any)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)

class CRUDBase(Generic[DBModelType, CreateSchemaType]):
    def __init__(self, model: DBModelType):
        self.model = model
        
    def get(self, db: Session, username: str) -> DBModelType:
        stmt = select(self.model).where(self.model.username == username)
        
        try:
            result = db.exec(stmt).one()
            return result
        except NoResultFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found") from e
        
    def create(self, db: Session, obj_in: CreateSchemaType) -> DBModelType:
        password_hash = get_password_hash(obj_in.password.get_secret_value()) # type: ignore
        user_obj = self.model(**dict(obj_in), password_hash=password_hash, created_at=datetime.datetime.now(datetime.UTC))
        
        try:
            user_dict = self.model.model_validate(user_obj, strict=True)
            db.add(user_dict)
            db.commit()
            db.refresh(user_dict)
            return user_dict
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists in database") from e
    
    def authenticate(self, db: Session, username: str, password: str) -> DBModelType:
        user_obj = self.get(db, username)
        is_pwd_valid = verify_password(password, user_obj.password_hash)
        if is_pwd_valid:
            user_obj.last_signed_in = datetime.datetime.now(datetime.UTC)
            db.add(user_obj)
            db.commit()
            db.refresh(user_obj)
            return user_obj
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized", headers={"WWW-Authenticate": "Bearer"})
