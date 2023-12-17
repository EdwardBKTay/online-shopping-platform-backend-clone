from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from schemas.product import ProductCreate, ProductUpdate
from services.crud_user import get_current_user, is_user_vendor
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session
from utils.deps import get_session
from db.models import Product, User
from typing import Annotated
import datetime

products_router = APIRouter()


@products_router.get("/{product_id}/", dependencies=[Depends(get_current_user)])
async def get_product(product_id: int, session: Annotated[Session, Depends(get_session)]):
    product_obj = session.get(Product, product_id)
    
    if product_obj is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product_obj

@products_router.post("/create/", status_code=201)
async def create_product(product: ProductCreate, session: Annotated[Session, Depends(get_session)], user: Annotated[User, Depends(is_user_vendor)]):
    product_obj = Product(**dict(product), created_at=datetime.datetime.now(datetime.UTC), vendor=user)
    try:
        product_dict = Product.model_validate(product_obj, strict=True)
        
        session.add(product_dict)
        session.commit()
        session.refresh(product_dict)
        return product_dict
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail="Product could not be created") from e
    
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail="Product name duplicated") from e

@products_router.put("/{product_id}/update/")
async def update_product(product_id: int, product: ProductUpdate, session: Annotated[Session, Depends(get_session)], user: Annotated[User, Depends(is_user_vendor)]):
    product_obj = session.get(Product, product_id)
    
    if product_obj is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product_obj.vendor_id != user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to update product")
    
    product_data = product.model_dump(exclude_unset=True)
    for key, value in product_data.items():
        setattr(product_obj, key, value)

    product_obj.updated_at = datetime.datetime.now(datetime.UTC)
    try:
        session.add(product_obj)
        session.commit()
        session.refresh(product_obj)
        return product_obj
    
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail="Product name duplicated") from e

@products_router.delete("/{product_id}/delete/")
async def delete_product(product_id: int, session: Annotated[Session, Depends(get_session)], user: Annotated[User, Depends(is_user_vendor)]):
    product_obj = session.get(Product, product_id)
    
    if product_obj is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product_obj.vendor_id != user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to delete product")
    
    session.delete(product_obj)
    session.commit()
    return {"message": "Product deleted successfully"}
