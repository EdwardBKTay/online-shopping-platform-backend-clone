from typing import Optional
from sqlmodel import SQLModel, Field, Column, DateTime
import datetime

class User(SQLModel, table=True): # type: ignore
    """
    User database model
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True)
    password_hash: str = Field(exclude=True)
    last_signed_in: Optional[datetime.datetime] = Field(sa_column=Column(DateTime(timezone=True), default=None))
    is_email_verified: bool = Field(default=False)
    created_at: datetime.datetime = Field(sa_column=Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.UTC)))
    updated_at: Optional[datetime.datetime] = Field(sa_column=Column(DateTime(timezone=True), onupdate=datetime.datetime.now(datetime.UTC), default=None))

class Vendor(SQLModel, table=True): # type: ignore
    """
    Vendor database model
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True)
    password_hash: str = Field(exclude=True)
    last_signed_in: Optional[datetime.datetime] = Field(sa_column=Column(DateTime(timezone=True), default=None))
    is_email_verified: bool = Field(default=False)
    created_at: datetime.datetime = Field(sa_column=Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.UTC)))
    updated_at: Optional[datetime.datetime] = Field(sa_column=Column(DateTime(timezone=True), onupdate=datetime.datetime.now(datetime.UTC), default=None))
