from pydantic import BaseModel, Field, PositiveInt
from typing import Optional, Annotated
from decimal import Decimal
from enum import Enum

class ProductCategory(str, Enum):
    electronics = "Electronics"
    clothing_and_fashion = "Clothing and Fashion"
    home_and_kitchen = "Home and Kitchen"
    books_and_literature = "Books and Literature"
    sports_and_fitness = "Sports and Fitness"
    toys_and_games = "Toys and Games"
    beauty_and_personal_care = "Beauty and Personal Care"
    health_and_household = "Health and Household"
    automotive = "Automotive"
    others = "Others"
    jewelry_and_accessories = "Jewelry and Accessories"
    groceries_and_food = "Groceries and Food"
    furniture_and_decor = "Furniture and Decor"
    pet_supplies = "Pet Supplies"
    tools_and_hardware = "Tools and Hardware"
    music_and_instruments = "Music and Instruments"

class ProductBase(BaseModel):
    name: str
    description: str
    category_name: ProductCategory
    original_price: Decimal = Field(..., ge=0, decimal_places=2)
    available_quantity: PositiveInt

class ProductCreate(ProductBase):
    pass

# https://github.com/pydantic/pydantic/pull/7311 using Annotated rather than Optional for Decimal
class ProductUpdate(ProductCreate):
    name: str | None = None
    description: str | None = None
    category_name: ProductCategory | None = None
    original_price: Annotated[Decimal, Field(..., ge=0, decimal_places=2)] | None = None
    available_quantity: PositiveInt | None = None
