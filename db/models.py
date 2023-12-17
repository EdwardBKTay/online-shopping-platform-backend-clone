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
    products: list["Product"] = Relationship(back_populates="vendor")

class Product(SQLModel, table=True):
    """
    Item database model
    """
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(unique=True)
    description: str = Field(default=None)
    price: float
    created_at: datetime.datetime = Field(sa_column=Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.UTC)))
    updated_at: Optional[datetime.datetime] = Field(sa_column=Column(DateTime(timezone=True), onupdate=datetime.datetime.now(datetime.UTC), default=None))
    quantity: int
    vendor_id: Optional[int] = Field(default=None, foreign_key="user.id")
    vendor: Optional[User] = Relationship(back_populates="products")
