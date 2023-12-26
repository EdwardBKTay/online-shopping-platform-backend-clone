import datetime

from sqlmodel import Session

from db.models import Category
from schemas.product import ProductCategory


def set_default_product_categories(db: Session):
    for category in ProductCategory:
        category_obj = Category(name=category, created_at=datetime.datetime.now(datetime.UTC))
        db.add(category_obj)
        db.commit()
