from typing import Optional, List
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
    updated_at: Optional[datetime.datetime] = Field(sa_column=Column(DateTime(timezone=True), default=None))
    is_vendor: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    auth_token: Optional[str] = Field(default=None)
    
    products: List["Product"] = Relationship(back_populates="vendor")
    carts: List["Cart"] = Relationship(back_populates="user")

class Product(SQLModel, table=True):
    """
    Item database model
    """
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(unique=True)
    description: str = Field(default=None)
    price: float = Field(default=0, ge=0)
    quantity: int = Field(default=0, ge=0)
    created_at: datetime.datetime = Field(sa_column=Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.UTC)))
    updated_at: Optional[datetime.datetime] = Field(sa_column=Column(DateTime(timezone=True), default=None))
    
    vendor_id: int = Field(foreign_key="user.id")
    vendor: User = Relationship(back_populates="products")
    orders: List["Cart"] = Relationship(back_populates="product")
    
class Cart(SQLModel, table=True):
    """
    Cart database model
    """
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    quantity: int = Field(gt=0)
    created_at: datetime.datetime = Field(sa_column=Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.UTC)))
    updated_at: Optional[datetime.datetime] = Field(sa_column=Column(DateTime(timezone=True), default=None))

    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="carts")
    product_id: int = Field(foreign_key="product.id")
    product: Product = Relationship(back_populates="orders")
