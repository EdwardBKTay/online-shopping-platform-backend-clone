import os

from functools import lru_cache

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

from core.config import settings
from schemas.user import UserState

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.TOKEN_URL)

@lru_cache(maxsize=1)
def read_public_key():
    current_dir = os.getcwd()
    public_key_path = os.path.join(current_dir, settings.PUBLIC_KEY_PATH)
    with open(public_key_path, "rb") as file:
        return file.read()
    
@lru_cache(maxsize=1)
def read_private_key():
    current_dir = os.getcwd()
    private_key_path = os.path.join(current_dir, settings.PRIVATE_KEY_PATH)
    with open(private_key_path, "rb") as file:
        return file.read()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)

def create_access_token(user_data: UserState, private_key: bytes) -> str:
    payload = user_data.model_dump().copy()
    encoded_token = jwt.encode(payload, private_key, algorithm=settings.ACCESS_TOKEN_ALGORITHM)
    return encoded_token

def create_refresh_token(user_data: UserState, secret_key: str) -> str:
    payload = user_data.model_dump().copy()
    encoded_token = jwt.encode(payload, secret_key, algorithm=settings.REFRESH_TOKEN_ALGORITHM)
    return encoded_token
