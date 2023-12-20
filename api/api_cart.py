from fastapi import APIRouter, Depends, HTTPException
from schemas.cart import CartCreate, CartUpdate
from services.crud_user import is_only_user
from db.models import Cart, Product, User, CartItem
from sqlmodel import Session, select
from utils.deps import get_session
from fastapi.encoders import jsonable_encoder
from typing_extensions import Annotated
import datetime

carts_router = APIRouter()

# TODO: checkout route for checking out the cart, integrate with payment gateway, stripe, etc. 
# https://medium.com/@chodvadiyasaurabh/integrating-stripe-payment-gateway-with-fastapi-a-comprehensive-guide-8fe4540b5a4

# @carts_router.get("/{username}/checkout/", status_code=200)
# async def checkout_cart(username: str, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(is_only_user)]):
#     if username != current_user.username:
#         raise HTTPException(status_code=403, detail="Unauthorized to checkout other user's cart")
    
#     cart = session.exec(select(Cart).where(Cart.user == current_user)).one_or_none()
    
#     if cart is None:
#         raise HTTPException(status_code=404, detail="Cart not found")
    
#     cart_items = session.exec(select(CartItem).where(CartItem.cart == cart)).all()
    
#     for cart_item in cart_items:
#         product = session.get(Product, cart_item.product_id)
#         if product is None:
#             raise HTTPException(status_code=404, detail="Product not found")
#         if product.available_quantity < cart_item.quantity:
#             raise HTTPException(status_code=409, detail="Not enough stock")
#         product.available_quantity -= cart_item.quantity
#         session.add(product)
#         session.delete(cart_item)
#         session.delete(cart)
    
#     session.commit()
#     return {"message": "Checkout successful"}

@carts_router.post("/{username}/add/{product_id}/", status_code=201)
async def add_to_cart(product_id: int, username: str, req: CartCreate, session: Annotated[Session, Depends(get_session)], user: Annotated[User, Depends(is_only_user)]):
    product = session.get(Product, product_id)
    
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.available_quantity < req.quantity:
        raise HTTPException(status_code=409, detail="Not enough stock")
    
    if username != user.username:
        raise HTTPException(status_code=403, detail="Unauthorized to add to other user's cart")
    
    stmt = select(Cart).where(Cart.user == user and Cart.cart_items.any(CartItem.product == product)) # type: ignore
    
    if session.exec(stmt).one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Product already in cart")
    
    user_cart = Cart(user=user, created_at=datetime.datetime.now(datetime.UTC))
    
    new_cart_item = CartItem(**jsonable_encoder(req), product=product, cart=user_cart, created_at=datetime.datetime.now(datetime.UTC))
    
    session.add(user_cart)
    session.add(new_cart_item)
    session.commit()
    session.refresh(new_cart_item)
    return new_cart_item

@carts_router.get("/{username}/", status_code=200)
async def get_user_cart(username: str, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(is_only_user)]):
    if username != current_user.username:
        raise HTTPException(status_code=403, detail="Unauthorized to view other user's cart")
    
    cart = session.exec(select(Cart).where(Cart.user == current_user)).one_or_none()
    
    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    return session.exec(select(CartItem).where(CartItem.cart == cart)).all()

@carts_router.put("/{username}/{cart_item_id}/update/", status_code=200)
async def update_cart_items(username: str, cart_item_id: int, req: CartUpdate, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(is_only_user)]):
    cart_item = session.get(CartItem, cart_item_id)
    
    if cart_item is None:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    if current_user.username != username or cart_item.cart.user.username != current_user.username:
        raise HTTPException(status_code=403, detail="Unauthorized to update other user's cart")
    
    product = session.get(Product, cart_item.product_id)
    
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    cart_item_data = req.model_dump(exclude_unset=True)
    for key, value in cart_item_data.items():
        if key == "quantity" and product.available_quantity < value:
            raise HTTPException(status_code=409, detail="Not enough stock")
        setattr(cart_item, key, value)
    
    cart_item.updated_at = datetime.datetime.now(datetime.UTC)
    
    session.add(cart_item)
    session.commit()
    session.refresh(cart_item)
    return cart_item

@carts_router.delete("/{username}/{cart_item_id}/delete/", status_code=204)
async def remove_cart_item(username: str, cart_item_id: int, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(is_only_user)]):
    cart_item = session.get(CartItem, cart_item_id)
    
    if cart_item is None:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    if current_user.username != username or cart_item.cart.user.username != username:
        raise HTTPException(status_code=403, detail="Unauthorized to delete other user's cart")
    
    product = session.get(Product, cart_item.product_id)
    
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    session.delete(cart_item)
    session.commit()
    return None
