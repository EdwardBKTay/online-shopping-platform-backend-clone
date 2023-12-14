from fastapi import HTTPException, status
from pydantic import BaseModel, Field, EmailStr, SecretStr, field_validator, field_serializer
from schemas.user import UserCreate
import re

class VendorCreate(UserCreate):
    pass
