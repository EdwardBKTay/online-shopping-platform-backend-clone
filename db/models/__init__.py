from sqlmodel import SQLModel, Field, Column, DateTime, Relationship
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# TODO: update the api response_model

class UserBase(SQLModel):
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

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    products: List["Product"] = Relationship(back_populates="vendor")
    cart: Optional["Cart"] = Relationship(back_populates="user")
    orders: List["Order"] = Relationship(back_populates="user")

class UserRead(UserBase):
    id: int
    
class ProductBase(SQLModel):
    name: str = Field(unique=True)
    description: str
    category_id: int = Field(foreign_key="category.id")
    category: "Category" = Relationship(back_populates="products")
    original_price: Decimal = Field(default=0, decimal_places=2, ge=0)
    available_quantity: int = Field(default=0, ge=0)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=None))
    
    vendor_id: int = Field(foreign_key="user.id")

class Product(SQLModel, table=True):
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
    order_items: List["OrderItem"] = Relationship(back_populates="product")

class ProductRead(ProductBase):
    id: int
    
class CategoryBase(SQLModel):
    name: str = Field(unique=True)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=None))

class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    
    products: List["Product"] = Relationship(back_populates="category")

class CategoryRead(CategoryBase):
    id: int
    
class CartBase(SQLModel):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=None))
    
class Cart(CartBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    
    user: Optional["User"] = Relationship(back_populates="cart")
    cart_items: List["CartItem"] = Relationship(back_populates="cart")

class CartRead(CartBase):
    id: int

class CartItemBase(SQLModel):
    cart_id: Optional[int] = Field(default=None, foreign_key="cart.id")
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    quantity: int = Field(default=0, ge=0)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=None))
    
class CartItem(CartItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    
    cart: Optional["Cart"] = Relationship(back_populates="cart_items")
    product: Optional["Product"] = Relationship(back_populates="cart_items")

class CartItemRead(CartItemBase):
    id: int
    
class OrderBase(SQLModel):
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=None))

class Order(OrderBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    
    user: User = Relationship(back_populates="orders")
    order_items: List["OrderItem"] = Relationship(back_populates="order")

class OrderRead(OrderBase):
    id: int

class OrderItemBase(SQLModel):
    order_id: Optional[int] = Field(default=None, foreign_key="order.id")
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    quantity: int = Field(default=0, ge=0)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=None))
    
class OrderItem(OrderItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    
    order: Optional["Order"] = Relationship(back_populates="order_items")
    product: Optional["Product"] = Relationship(back_populates="order_items")

class OrderItemRead(OrderItemBase):
    id: int
    



