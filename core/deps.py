from pydantic import ValidationError
from db.engine import get_db, DB_URL
from sqlmodel import Session
from typing import Annotated
from fastapi import Depends, HTTPException
from auth.auth import oauth2_scheme, ALGORITHM, TokenPayload, read_public_key
from jose import jwt, JWTError
from crud.crud_user import user
import datetime

def get_session():
    engine = get_db(DB_URL, {"echo": True})
    with Session(engine) as session:
        yield session

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_session)):
    http_exception = HTTPException(status_code=401, detail="Invalid authentication credentials", headers={"WWW-Authenticate": "Bearer"})
    
    try: 
        public_key = read_public_key()
        payload = jwt.decode(token, public_key, algorithms=[ALGORITHM])
        token_data = TokenPayload.model_validate(payload, strict=True)
        
        if token_data is None:
            raise http_exception
        
        if token_data.username is None and token_data.email is None:
            raise http_exception
        
        user_obj = user.get_username(session, token_data.username)
        user_obj.last_signed_in = datetime.datetime.now(datetime.UTC)
        
        session.add(user_obj)
        session.commit()
    
        if user_obj is None:
            raise http_exception
    
    except JWTError as e:
        raise http_exception from e
            
    return user_obj
