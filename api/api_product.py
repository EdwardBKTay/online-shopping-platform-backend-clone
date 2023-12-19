from fastapi import APIRouter, Depends, HTTPException, Query
from schemas.product import ProductCreate, ProductUpdate
from services.crud_user import get_current_user, is_user_vendor
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from utils.deps import get_session
from db.models import Product, User, Category
from typing import Annotated
import datetime

products_router = APIRouter()

@products_router.post("/create/", status_code=201)
async def create_new_product(req: ProductCreate, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(is_user_vendor)]):
    category = session.exec(select(Category).where(Category.name == req.category_name)).one()
    
    new_product = Product(**jsonable_encoder(req), created_at=datetime.datetime.now(datetime.UTC), vendor=current_user, category=category)
    
    try:
        session.add(new_product)
        session.commit()
        return new_product
    
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=409, detail="Product name duplicated") from e
    
@products_router.get("/search/", dependencies=[Depends(get_current_user)])
async def search_products(session: Annotated[Session, Depends(get_session)], q: str | None = None, offset: int  = 0, limit: int = Query(default=10, le=10)):
    if q is None:
        return []
    stmt = select(Product).where(Product.name.ilike(f"%{q}%")).order_by(Product.name).offset(offset).limit(limit) # type: ignore
    products = session.exec(stmt).all()
    return products
    
@products_router.put("/{product_id}/update/")
async def update_product(product_id: int, req: ProductUpdate, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(is_user_vendor)]):
    product_obj = session.get(Product, product_id)
    
    if product_obj is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product_obj.vendor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to update product")
    
    category_obj = session.exec(select(Category).where(Category.name == req.category_name)).one_or_none()
    product_data = req.model_dump(exclude_unset=True)
    for key, value in product_data.items():
        setattr(product_obj, key, value)
    product_obj.updated_at = datetime.datetime.now(datetime.UTC)
    product_obj.category = category_obj
    
    try:
        session.add(product_obj)
        session.commit()
        session.refresh(product_obj)
        return product_obj
    
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=409, detail="Product name duplicated") from e

@products_router.delete("/{product_id}/delete/", status_code=204)
async def delete_product(product_id: int, session: Annotated[Session, Depends(get_session)], user: Annotated[User, Depends(is_user_vendor)]):
    product_obj = session.get(Product, product_id)
    
    if product_obj is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product_obj.vendor_id != user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to delete product")
    
    session.delete(product_obj)
    session.commit()
    return

@products_router.get("/{product_id}/", dependencies=[Depends(get_current_user)])
async def get_product(product_id: int, session: Annotated[Session, Depends(get_session)]):
    product_obj = session.get(Product, product_id)
    
    if product_obj is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product_obj

@products_router.get("/", dependencies=[Depends(get_current_user)])
async def get_products(session: Annotated[Session, Depends(get_session)], offset: int = 0, limit: int = Query(default=100, le=100)):
    products = session.exec(select(Product).offset(offset).limit(limit)).all()
    return products
