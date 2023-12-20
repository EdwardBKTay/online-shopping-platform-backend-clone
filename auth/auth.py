from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt
from schemas.user import UserState
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

ACCESS_TOKEN_EXPIRATION_MINUTES = 15
REFRESH_TOKEN_EXPIRATION_MINUTES = 60 * 24 * 7
ALGORITHM = "RS256"

def read_public_key():
    current_dir = os.getcwd()
    public_key_path = os.path.join(current_dir, "public_key.pem")
    with open(public_key_path, "rb") as file:
        return file.read()
    
def read_private_key():
    current_dir = os.getcwd()
    private_key_path = os.path.join(current_dir, "private_key.pem")
    with open(private_key_path, "rb") as file:
        return file.read()

public_key = read_public_key()
private_key = read_private_key()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)

def create_access_token(user_data: UserState, private_key: bytes) -> str:
    payload = user_data.model_dump().copy()
    encoded_token = jwt.encode(payload, private_key, algorithm=ALGORITHM)
    return encoded_token

def create_refresh_token(user_data: UserState, secret_key: str) -> str:
    payload = user_data.model_dump().copy()
    encoded_token = jwt.encode(payload, secret_key, algorithm="HS256")
    return encoded_token
