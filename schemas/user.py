import re
from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError
from pydantic import EmailStr, SecretStr, field_serializer, Field, field_validator, SecretStr, BaseModel
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(pattern=r"^[a-zA-Z0-9]+$", min_length=3, max_length=20)
    email: EmailStr

class UserCreate(UserBase):
    password: SecretStr
    is_vendor: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: SecretStr) -> SecretStr:
        str_pwd = v.get_secret_value()
        re_compile = re.compile(r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[@$!%*?&^_-])\S{8,}$")
        is_valid = re.fullmatch(re_compile, str_pwd)
        if is_valid is None:
            raise RequestValidationError([{"loc": ["password"], "msg": "Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, one number, and one special character", "type": "value_error"}])
        return v
    
    @field_serializer("password", when_used="json")
    def dump_secret(self, v: SecretStr):
        return v.get_secret_value()

class UserState(BaseModel):
    username: str
    email: EmailStr
    is_vendor: bool
    is_superuser: bool
    exp: datetime | int
