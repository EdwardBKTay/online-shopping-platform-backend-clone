from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt
import os
from schemas.token import TokenPayload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ACCESS_TOKEN_EXPIRATION_MINUTES = 60
ALGORITHM = "RS256"

def read_public_key():
    current_dir = os.getcwd()
    print(current_dir)
    public_key_path = os.path.join(current_dir, "public_key.pem")
    with open(public_key_path, "rb") as file:
        return file.read()
    
read_public_key()
    
def read_private_key():
    current_dir = os.getcwd()
    private_key_path = os.path.join(current_dir, "private_key.pem")
    with open(private_key_path, "rb") as file:
        return file.read()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)

def create_access_token(user_data: TokenPayload) -> str:
    try:
        private_key = read_private_key()
    except Exception as e:
        raise Exception(f"Unable to read private key: {e}") from e
    
    payload = user_data.model_dump().copy()
    encoded_token = jwt.encode(payload, private_key, algorithm=ALGORITHM)
    return encoded_token
