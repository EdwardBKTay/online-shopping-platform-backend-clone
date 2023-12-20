# Database design reference: https://appmaster.io/blog/how-to-design-a-shopping-cart-database

from typing import Optional, List
from sqlmodel import SQLModel, Field, Column, Relationship, DateTime
from decimal import Decimal
from datetime import datetime

class User(SQLModel, table=True):
    """
    User database model
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True)
    password_hash: str = Field(exclude=True)
    last_signed_in: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), default=None))
    is_email_verified: bool = Field(default=False)
    created_at: datetime =  Field(sa_column=Column(DateTime(timezone=True)))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=None))
    is_vendor: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    auth_token: Optional[str] = Field(default=None)
    refresh_token: Optional[str] = Field(default=None)
    # reset_password_token: Optional[str] = Field(default=None)
    products: List["Product"] = Relationship(back_populates="vendor")
    cart: Optional["Cart"] = Relationship(back_populates="user")

class Product(SQLModel, table=True):
    """
    Item database model
    """
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(unique=True)
    description: str
    category_id: int = Field(foreign_key="category.id")
    category: "Category" = Relationship(back_populates="products")
    original_price: Decimal = Field(default=0, decimal_places=2, ge=0)
    available_quantity: int = Field(default=0, ge=0)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=None))
    vendor_id: int = Field(foreign_key="user.id")
    vendor: User = Relationship(back_populates="products")
    cart_items: List["CartItem"] = Relationship(back_populates="product")

class Category(SQLModel, table=True):
    """
    Category database model having a one-to-many relationship with Product
    """
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(unique=True)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=None))
    products: List[Product] = Relationship(back_populates="category")
    
class Cart(SQLModel, table=True):
    """
    Cart table that ties a specific user to a collection of products that they have added to their cart
    """
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="cart")
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=None))
    cart_items: List["CartItem"] = Relationship(back_populates="cart")
    
class CartItem(SQLModel, table=True):
    """
    Cart items table that ties a specific product to a specific shopping cart
    """
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    cart_id: int = Field(foreign_key="cart.id")
    cart: Cart = Relationship(back_populates="cart_items")
    product_id: int = Field(foreign_key="product.id")
    product: Product = Relationship(back_populates="cart_items")
    quantity: int = Field(gt=0)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=None))

# class Order(SQLModel):
#     """
#     Order database model for deals that have checked out
#     """
#     id: Optional[int] = Field(default=None, primary_key=True, index=True)
#     user_id: int = Field(foreign_key="user.id")
#     user: User = Relationship(back_populates="orders")
#     created_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
#     updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=None))
#     order_items: List["OrderItem"] = Relationship(back_populates="order")

# class OrderItem(SQLModel):
#     """
#     Order items table that ties a specific product to a specific order
#     """
#     id: Optional[int] = Field(default=None, primary_key=True, index=True)
#     order_id: int = Field(foreign_key="order.id")
#     order: Order = Relationship(back_populates="order_items")
#     product_id: int = Field(foreign_key="product.id")
#     product: Product = Relationship(back_populates="order_items")
#     quantity: int = Field(gt=0)
#     created_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
#     updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=None))
