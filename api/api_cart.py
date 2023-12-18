from fastapi import APIRouter, Depends, HTTPException
from schemas.cart import CartCreate, CartUpdate
from services.crud_user import is_only_user
from db.models import Cart, Product, User
from sqlmodel import Session, select
from utils.deps import get_session
from fastapi.encoders import jsonable_encoder
from typing_extensions import Annotated
import datetime

carts_router = APIRouter()

@carts_router.post("/add/", status_code=201)
async def add_to_cart(req: CartCreate, session: Annotated[Session, Depends(get_session)], user: Annotated[User, Depends(is_only_user)]):
    product = session.get(Product, req.product_id)
    
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.quantity < req.quantity:
        raise HTTPException(status_code=409, detail="Not enough stock")
    
    stmt = select(Cart).where(Cart.user == user and Cart.product == product)
    
    if session.exec(stmt).one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Product already in cart")
    
    new_obj = Cart(**jsonable_encoder(req), user=user, product=product, created_at=datetime.datetime.now(datetime.UTC))
    
    product.quantity -= req.quantity
    session.add(product)
    session.add(new_obj)
    session.commit()
    session.refresh(new_obj)
    return new_obj

@carts_router.get("/", status_code=200)
async def get_user_cart(session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(is_only_user)]):
    stmt = select(Cart).where(Cart.user == current_user)
    return session.exec(stmt).all()

@carts_router.put("/{cart_id}/update", status_code=200)
async def update_cart_items(cart_id: int, req: CartUpdate, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(is_only_user)]):
    cart_obj = session.get(Cart, cart_id)
    
    if cart_obj is None:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    if cart_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to update cart")
    
    product = session.get(Product, cart_obj.product_id)
    
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.quantity < req.quantity:
        raise HTTPException(status_code=409, detail="Not enough stock")
    
    cart_data = req.model_dump(exclude_unset=True)
    for key, value in cart_data.items():
        setattr(cart_obj, key, value)
    
    cart_obj.updated_at = datetime.datetime.now(datetime.UTC)
    
    product.quantity = product.quantity + cart_obj.quantity - req.quantity
    
    session.add(product)
    session.add(cart_obj)
    session.commit()
    session.refresh(cart_obj)
    return cart_obj

@carts_router.delete("/{cart_id}/delete", status_code=204)
async def delete_cart_items(cart_id: int, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(is_only_user)]):
    cart_obj = session.get(Cart, cart_id)
    
    if cart_obj is None:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    if cart_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to delete cart")
    
    product = session.get(Product, cart_obj.product_id)
    
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.quantity += cart_obj.quantity
    
    session.add(product)
    session.delete(cart_obj)
    session.commit()
    return None
