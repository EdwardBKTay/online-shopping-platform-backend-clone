from fastapi import APIRouter, Depends, HTTPException, Query
from schemas.product import ProductCreate, ProductUpdate, ProductAddToCart
from services.crud_user import get_current_user, is_only_user, is_user_vendor
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from utils.deps import get_session
from db.models import CartItemReadAll, Product, User, Category, ProductReadWithVendor, Cart, CartItem
from typing import Annotated, Sequence
import datetime

products_router = APIRouter()

@products_router.post("/create/", status_code=201, response_model=ProductReadWithVendor)
async def create_new_product(req: ProductCreate, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(is_user_vendor)]):
    category = session.exec(select(Category).where(Category.name == req.category_name)).one()
    
    new_product = Product(**jsonable_encoder(req), created_at=datetime.datetime.now(datetime.UTC), vendor=current_user, category=category)
    
    try:
        session.add(new_product)
        session.commit()
        session.refresh(new_product)
        return new_product
    
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=409, detail="Product name duplicated") from e
    
@products_router.get("/search/", dependencies=[Depends(get_current_user)], response_model=Sequence[ProductReadWithVendor])
async def search_products(session: Annotated[Session, Depends(get_session)], product_name: str | None = None, category: str | None = None, offset: int  = 0, limit: int = Query(default=10, le=10)):
    if product_name is None and category is None:
        return []
    elif product_name is not None and category is None:
        stmt = select(Product).where(Product.name.ilike(f"%{product_name}%")).order_by(Product.name).offset(offset).limit(limit) # type: ignore
    elif product_name is None and category is not None:
        stmt = select(Product).where(Product.category.has(Category.name.ilike(f"%{category}%"))).order_by(Product.name).offset(offset).limit(limit) # type: ignore
    else:
        stmt = select(Product).where(Product.name.ilike(f"%{product_name}%")).where(Product.category.has(Category.name.ilike(f"%{category}%"))).order_by(Product.name).offset(offset).limit(limit) # type: ignore
        
    products = session.exec(stmt).all()
    return products

@products_router.get("/category/", dependencies=[Depends(get_current_user)], response_model=Sequence[ProductReadWithVendor])
async def filter_product_by_category(session: Annotated[Session, Depends(get_session)], category: str | None = None):
    if category is None:
        return []
    
    if session.exec(select(Category).where(Category.name == category)).one_or_none() is None:
        raise HTTPException(status_code=404, detail="Category not found")
        
    stmt = select(Product).where(Product.category.has(Category.name == category)).order_by(Product.name)
    products = session.exec(stmt).all()
    return products

@products_router.put("/{product_id}/update/", status_code=200, response_model=ProductReadWithVendor)
async def update_product(product_id: int, req: ProductUpdate, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(is_user_vendor)]):
    product_obj = session.get(Product, product_id)
    
    if product_obj is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product_obj.vendor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to update product")
    
    product_data = req.model_dump(exclude_unset=True)
    for key, value in product_data.items():
        if key == "category_name":
            continue
        setattr(product_obj, key, value)
        
    if req.category_name is not None:
        category_obj = session.exec(select(Category).where(Category.name == req.category_name)).one_or_none()
        if category_obj is None:
            raise HTTPException(status_code=404, detail="Category not found")
        
        product_obj.category = category_obj

    product_obj.updated_at = datetime.datetime.now(datetime.UTC)
    
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

@products_router.get("/{product_id}/", dependencies=[Depends(get_current_user)], response_model=ProductReadWithVendor)
async def get_product(product_id: int, session: Annotated[Session, Depends(get_session)]):
    product_obj = session.get(Product, product_id)
    
    if product_obj is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product_obj

@products_router.get("/", dependencies=[Depends(get_current_user)], response_model=Sequence[ProductReadWithVendor])
async def get_products(session: Annotated[Session, Depends(get_session)], offset: int = 0, limit: int = Query(default=100, le=100)):
    products = session.exec(select(Product).offset(offset).limit(limit)).all()
    return products

@products_router.post("/{product_id}/add-to-cart/", status_code=201, response_model=CartItemReadAll)
async def add_to_cart(product_id: int, req: ProductAddToCart, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(is_only_user)]):
    product = session.get(Product, product_id)
    
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.available_quantity < req.quantity:
        raise HTTPException(status_code=409, detail="Not enough stock")
    
    user_cart = session.exec(select(Cart).where(Cart.user == current_user)).one_or_none()
    
    if user_cart is None:
        user_cart = Cart(user=current_user, created_at=datetime.datetime.now(datetime.UTC))
        session.add(user_cart)
        session.commit()
        session.refresh(user_cart)
    
    cart_item = session.exec(select(CartItem).where(CartItem.cart == user_cart and CartItem.product_id == product_id)).one_or_none()
    
    if cart_item is None:
        new_cart_item = CartItem(cart=user_cart, product_id=product_id, quantity=req.quantity, created_at=datetime.datetime.now(datetime.UTC))
    else:
        raise HTTPException(status_code=409, detail="Product already in cart")
    
    user_cart.updated_at = datetime.datetime.now(datetime.UTC)
    
    session.add(user_cart)
    session.add(new_cart_item)
    session.commit()
    session.refresh(new_cart_item)
    return new_cart_item
