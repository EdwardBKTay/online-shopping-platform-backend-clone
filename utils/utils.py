from fastapi import Depends
from sqlmodel import Session
from db.models import Category
from typing import Annotated
import datetime

def set_default_product_categories(db: Session):
    default_categories = ["Electronics", "Clothing and Fashion", "Home and Kitchen", "Books and Literature", "Sports and Fitness", "Toys and Games", "Beauty and Personal Care", "Health and Household", "Automotive", "Others", "Jewelry and Accessories", "Groceries and Food", "Furniture and Decor", "Pet Supplies", "Tools and Hardware", "Music and Instruments"]
    
    for category in default_categories:
        category_obj = Category(name=category, created_at=datetime.datetime.now(datetime.UTC))
        db.add(category_obj)
        db.commit()
