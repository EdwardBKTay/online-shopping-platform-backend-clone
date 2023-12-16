import re
from fastapi import HTTPException, status
from pydantic import EmailStr, SecretStr, field_serializer, Field, field_validator, SecretStr

from utils.crud_base import CreateSchemaBaseModel

class UserBase(CreateSchemaBaseModel):
    username: str = Field(pattern=r"^[a-zA-Z0-9]+$", min_length=3, max_length=20)
    email: EmailStr

class UserCreate(UserBase): 
    password: SecretStr
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: SecretStr) -> SecretStr:
        str_pwd = v.get_secret_value()
        re_compile = re.compile(r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[@$!%*?&^_-])\S{8,}$")
        is_valid = re.fullmatch(re_compile, str_pwd)
        if is_valid is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST ,detail="Password must contain at least 8 characters, including at least one uppercase letter, one lowercase letter, one digit, one special character (@$!%*?&^_-), and no whitespace.")
        return v
    
    @field_serializer("password", when_used="json")
    def dump_secret(self, v: SecretStr):
        return v.get_secret_value()
