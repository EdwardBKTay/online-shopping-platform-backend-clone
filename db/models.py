from typing import Optional
from sqlmodel import SQLModel, Field, Column, DateTime
import datetime

class ModelBase(SQLModel):
    """
    Base class for database models
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime.datetime = Field(sa_column=Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.UTC)))
    updated_at: Optional[datetime.datetime] = Field(sa_column=Column(DateTime(timezone=True), onupdate=datetime.datetime.now(datetime.UTC), default=None))

class UserModelBase(ModelBase):
    """
    User database model
    """
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True)
    password_hash: str = Field(exclude=True)
    last_signed_in: Optional[datetime.datetime] = Field(sa_column=Column(DateTime(timezone=True), default=None))
    is_email_verified: bool = Field(default=False)
    
class User(UserModelBase, table=True): # type: ignore
    pass

# class VendorModelBase(ModelBase): 
#     vendor_name: str = Field(unique=True, index=True)
#     email: str = Field(unique=True)
#     password_hash: str = Field(exclude=True)
#     last_signed_in: Optional[datetime.datetime] = Field(sa_column=Column(DateTime(timezone=True), default=None))
#     is_email_verified: bool = Field(default=False)

# class Vendor(VendorModelBase, table=True): # type: ignore
#     pass
