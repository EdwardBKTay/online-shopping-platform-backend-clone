from pydantic import BaseModel
from schemas.user import UserBase
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(UserBase):
    exp: datetime
