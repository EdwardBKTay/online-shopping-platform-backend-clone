from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlmodel import Column, DateTime, Field, Relationship, SQLModel


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
    auth_token: Optional[str] = Field(default=None, exclude=True)
    refresh_token: Optional[str] = Field(default=None, exclude=True)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    products: List["Product"] = Relationship(back_populates="vendor")
    cart: Optional["Cart"] = Relationship(back_populates="user")
    orders: List["Order"] = Relationship(back_populates="user")

class UserRead(UserBase):
    id: int
    
class UserReadWithProduct(UserRead):
    products: List["ProductRead"] = []
    
class UserReadWithCart(UserRead):
    cart: Optional["CartRead"] = None
    
class UserReadWithOrder(UserRead):
    orders: List["OrderRead"] = []
    

class ProductBase(SQLModel):
    name: str = Field(unique=True)
    description: str
    category_id: int = Field(foreign_key="category.id")
    original_price: Decimal = Field(default=0, decimal_places=2, ge=0)
    available_quantity: int = Field(default=0, ge=0)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=None))
    
    vendor_id: int = Field(foreign_key="user.id")

class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    
    vendor: User = Relationship(back_populates="products")
    cart_items: List["CartItem"] = Relationship(back_populates="product")
    order_items: List["OrderItem"] = Relationship(back_populates="product")
    category: "Category" = Relationship(back_populates="products")

class ProductRead(ProductBase):
    id: int
    
class ProductReadWithVendor(ProductRead):
    vendor: UserRead
    
class ProductReadWithCartItems(ProductRead):
    cart_items: List["CartItemRead"] = []
    
class CategoryBase(SQLModel):
    name: str = Field(unique=True)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=None))

class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    
    products: List["Product"] = Relationship(back_populates="category")

class CategoryRead(CategoryBase):
    id: int
    
    products: List["ProductRead"] = []
    
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
    
class CartReadWithUser(CartRead):
    user: Optional[UserRead] = None
    
class CartReadWithCartItems(CartRead):
    cart_items: List["CartItemRead"] = []
    
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
    
class CartItemReadWithCart(CartItemRead):
    cart: Optional[CartRead] = None
    
class CartItemReadWithProduct(CartItemRead):
    product: Optional[ProductRead] = None
    
class CartItemReadAll(CartItemRead):
    cart: Optional[CartRead] = None
    product: Optional[ProductRead] = None
    
class OrderBase(SQLModel):
    total_price: Decimal = Field(default=0, decimal_places=2, ge=0)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), default=None))

class Order(OrderBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    
    user: User = Relationship(back_populates="orders")
    order_items: List["OrderItem"] = Relationship(back_populates="order")

class OrderRead(OrderBase):
    id: int
    
    user: UserRead
    order_items: List["OrderItemReadWithProduct"] = []

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

class OrderItemReadWithOrder(OrderItemRead):
    order: Optional[OrderRead] = None
    
class OrderItemReadWithProduct(OrderItemRead):
    product: Optional[ProductRead] = None

class UserReadAll(UserRead):
    products: List[ProductRead] = []
    cart: Optional[CartReadWithCartItems] = None
    orders: List[OrderRead] = []
    
class CartReadAll(CartRead):
    user: Optional[UserRead] = None
    cart_items: List[CartItemReadWithProduct] = []

class EmailVerificationBase(SQLModel):
    email: str = Field(unique=True)
    token: str = Field(unique=True)
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    
class EmailVerification(EmailVerificationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
