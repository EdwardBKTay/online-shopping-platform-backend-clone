from typing import Optional
from sqlmodel import SQLModel, Field, Column, DateTime, Relationship
import datetime

class User(SQLModel, table=True):
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
    is_vendor: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    auth_token: Optional[str] = Field(default=None)
    items: list["Item"] = Relationship(back_populates="vendor")

class Item(SQLModel, table=True):
    """
    Item database model
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str = Field(default=None)
    price: float = Field()
    created_at: datetime.datetime = Field(sa_column=Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.UTC)))
    updated_at: Optional[datetime.datetime] = Field(sa_column=Column(DateTime(timezone=True), onupdate=datetime.datetime.now(datetime.UTC), default=None))
    quantity: int
    is_available: bool = Field(default=True)
    vendor_id: Optional[int] = Field(default=None, foreign_key="user.id")
    vendor: Optional[User] = Relationship(back_populates="items")
