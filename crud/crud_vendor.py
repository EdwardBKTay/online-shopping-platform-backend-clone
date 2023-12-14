from crud.base import CRUDBase
from db.models import Vendor
from schemas.vendor import VendorCreate
from sqlmodel import Session, select
from fastapi import HTTPException, status
from sqlalchemy.exc import NoResultFound, IntegrityError
from auth.auth import get_password_hash, verify_password
import datetime


class CRUDVendor(CRUDBase[Vendor]):
    def get_vendor_username(self, db: Session, username: str):
        stmt = select(Vendor).where(Vendor.vendor_username == username)
        
        try:
            result = db.exec(stmt).one()
            return result
        except NoResultFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found") from e
        
    def create(self, db: Session, obj_in: VendorCreate) -> Vendor:
        password_hash = get_password_hash(obj_in.password.get_secret_value())
        user_obj = Vendor(**dict(obj_in), password_hash=password_hash, created_at=datetime.datetime.now(datetime.UTC))
        
        try:
            user_dict = Vendor.model_validate(user_obj, strict=True)
            db.add(user_dict)
            db.commit()
            db.refresh(user_dict)
            return user_dict
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Vendor already exists in database") from e
        
    def authenticate_vendor(self, db: Session, username: str, password: str) -> Vendor:
        vendor_obj = self.get_vendor_username(db, username)
        is_pwd_valid = verify_password(password, vendor_obj.password_hash)
        if is_pwd_valid:
            vendor_obj.last_signed_in = datetime.datetime.now(datetime.UTC)
            db.add(vendor_obj)
            db.commit()
            db.refresh(vendor_obj)
            return vendor_obj
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Vendor Unauthorized", headers={"WWW-Authenticate": "Bearer"})

vendor = CRUDVendor(Vendor)
