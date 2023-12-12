from db.models import User
from sqlmodel import Session, select
from auth.auth import get_password_hash, verify_password
from crud.base import CRUDBase
from sqlalchemy.exc import IntegrityError, NoResultFound
from fastapi import HTTPException, status
import datetime
from schemas.user import UserCreate
from typing import Any

class CRUDUser(CRUDBase[User]):
    def get_username(self, db: Session, username: str):
        stmt = select(User).where(User.username == username)
        try:
            result = db.exec(stmt).one()
            return result
        except NoResultFound as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") from e

    def create(self, db: Session, obj_in: UserCreate) -> User:
        print(obj_in.password.get_secret_value())
        password_hash = get_password_hash(obj_in.password.get_secret_value())
        user_obj = User(**dict(obj_in), password_hash=password_hash, created_at=datetime.datetime.now(datetime.UTC))
        try:
            user_dict = User.model_validate(user_obj, strict=True)
            db.add(user_dict)
            db.commit()
            db.refresh(user_dict)
            return user_dict
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists in database") from e
        
    async def authenticate(self, db: Session, username: str, password: str):
        user_obj = self.get_username(db, username)
        is_pwd_valid = verify_password(password, user_obj.password_hash)
        if is_pwd_valid:
            user_obj.last_signed_in = datetime.datetime.now(datetime.UTC)
            db.add(user_obj)
            db.commit()
            return user_obj
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized", headers={"WWW-Authenticate": "Bearer"})

user = CRUDUser(User)
