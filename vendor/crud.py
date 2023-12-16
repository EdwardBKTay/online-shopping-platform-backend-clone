from db.models import Vendor
from utils.crud_base import CRUDBase
from vendor.schema import VendorCreate
from typing import Annotated
from fastapi import Depends, HTTPException
from sqlmodel import Session
from core.deps import get_session
from auth.auth import vendor_oauth2_scheme, ALGORITHM, read_public_key
from jose import jwt, ExpiredSignatureError, JWTError
from pydantic import ValidationError
from utils.token_schema import TokenPayload
import datetime



class CRUDVendor(CRUDBase[Vendor, VendorCreate]):
    def get_current_vendor(self, public_key: Annotated[bytes, Depends(read_public_key)], token: Annotated[str, Depends(vendor_oauth2_scheme)], session: Session = Depends(get_session)):
        http_exception = HTTPException(status_code=401, detail="Invalid authentication credentials", headers={"WWW-Authenticate": "Bearer"})
        
        payload = jwt.decode(token, public_key, algorithms=[ALGORITHM], options={"verify_signature": True})
        
        try:
            token_data = TokenPayload.model_validate(payload, strict=True)
            db_obj = self.get_username(session, token_data.username)
            
            if db_obj is None:
                raise http_exception
            
            db_obj.last_signed_in = datetime.datetime.now(datetime.UTC)
            session.add(db_obj)
            session.commit()

        except ValidationError as e:
            raise http_exception from e
        
        except ExpiredSignatureError as e:
            raise HTTPException(status_code=401, detail="Token has expired", headers={"WWW-Authenticate": "Bearer"}) from e
        
        except JWTError as e:
            raise http_exception from e
        
        return db_obj

vendor = CRUDVendor(Vendor)
