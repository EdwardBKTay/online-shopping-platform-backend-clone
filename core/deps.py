from pydantic import ValidationError
from db.engine import get_db, DB_URL
from sqlmodel import Session
from typing import Annotated
from fastapi import Depends, HTTPException, Header
from auth.auth import oauth2_scheme, ALGORITHM, TokenPayload, read_public_key
from jose import jwt, JWTError, ExpiredSignatureError
from crud.crud_user import user
from crud.crud_vendor import vendor
import datetime

def get_session():
    engine = get_db(DB_URL, {"echo": True})
    with Session(engine) as session:
        yield session
        
# rewrite get_current_entity to use the new TokenPayload model
def get_current_entity(token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_session), is_vendor: bool = Header(False)):
    http_exception = HTTPException(status_code=401, detail="Invalid authentication credentials", headers={"WWW-Authenticate": "Bearer"})
    
    try:
        public_key = read_public_key()
        payload = jwt.decode(token, public_key, algorithms=[ALGORITHM], options={"verify_signature": True})
        token_data = TokenPayload.model_validate(payload, strict=True)
        
        if token_data is None:
            raise http_exception
        
        if token_data.username is None and token_data.email is None:
            raise http_exception
        
        if is_vendor:
            entity_obj = vendor.get(session, token_data.username)
        else:
            entity_obj = user.get(session, token_data.username)
            
        if entity_obj is None:
            raise http_exception
            
        entity_obj.last_signed_in = datetime.datetime.now(tz=datetime.UTC)
        
        session.add(entity_obj)
        session.commit()
        
    except ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail="Token has expired", headers={"WWW-Authenticate": "Bearer"}) from e
        
    except JWTError as e:
        raise http_exception from e
    
    return entity_obj
