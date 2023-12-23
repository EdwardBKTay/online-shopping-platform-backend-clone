from fastapi import APIRouter, Depends, HTTPException
from schemas.cart import CartCreate, CartUpdate
from services.crud_user import is_only_user
from db.models import Cart, Product, User, CartItem, Order, OrderItem, OrderRead, CartItemReadAll
from sqlmodel import Session, select
from utils.deps import get_session
from fastapi.encoders import jsonable_encoder
from typing_extensions import Annotated, Sequence
from decimal import Decimal
import datetime

carts_router = APIRouter()

# https://medium.com/@chodvadiyasaurabh/integrating-stripe-payment-gateway-with-fastapi-a-comprehensive-guide-8fe4540b5a4

@carts_router.get("/{username}/checkout/", status_code=200, response_model=OrderRead)
async def checkout_cart(username: str, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(is_only_user)]):
    if username != current_user.username:
        raise HTTPException(status_code=403, detail="Unauthorized to checkout other user's cart")
    
    user_cart = session.exec(select(Cart).where(Cart.user == current_user)).one_or_none()
    
    if user_cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart_items = session.exec(select(CartItem).where(CartItem.cart == user_cart)).all()
    
    if len(cart_items) == 0:
        raise HTTPException(status_code=404, detail="Cart is empty")
    
    user_order = Order(user=current_user, created_at=datetime.datetime.now(datetime.UTC)) # type: ignore
    
    session.add(user_order)
    session.commit()
    session.refresh(user_order)
    
    total_price = 0
    
    for item in cart_items:
        product = session.get(Product, item.product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        if product.available_quantity < item.quantity:
            raise HTTPException(status_code=409, detail="Not enough stock")
        product.available_quantity -= item.quantity
        total_price += product.original_price * item.quantity
        
        order_item = OrderItem(quantity=item.quantity, product=product, order=user_order, created_at=datetime.datetime.now(datetime.UTC))
        
        session.add(order_item)
        session.add(product)
        session.delete(item)
    
    user_order.total_price = Decimal(total_price).quantize(Decimal("0.01"))
    session.add(user_order)
    session.delete(user_cart)
    session.commit()
    session.refresh(user_order)
    return user_order

@carts_router.post("/{username}/add/{product_id}/", status_code=201, response_model=CartItemReadAll)
async def add_to_cart(product_id: int, username: str, req: CartCreate, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(is_only_user)]):
    if username != current_user.username:
        raise HTTPException(status_code=403, detail="Unauthorized to add to other user's cart")
    
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
        
    stmt = select(Cart).join(CartItem).where(CartItem.product_id == product_id and Cart.user == current_user)
        
    if session.exec(stmt).one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Product already in cart")
    
    new_cart_item = CartItem(**jsonable_encoder(req), product=product, cart=user_cart, created_at=datetime.datetime.now(datetime.UTC))
    user_cart.updated_at = datetime.datetime.now(datetime.UTC)
    
    session.add(user_cart)
    session.add(new_cart_item)
    session.commit()
    session.refresh(new_cart_item)
    return new_cart_item

@carts_router.get("/{username}/", status_code=200, response_model=Sequence[CartItemReadAll])
async def get_user_cart(username: str, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(is_only_user)]):
    if username != current_user.username:
        raise HTTPException(status_code=403, detail="Unauthorized to view other user's cart")
    
    cart = session.exec(select(Cart).where(Cart.user == current_user)).one_or_none()
    
    if cart is not None:
        cart_items = session.exec(select(CartItem).where(CartItem.cart == cart)).all()

    else:
        user_cart = Cart(user=current_user, created_at=datetime.datetime.now(datetime.UTC))
        session.add(user_cart)
        session.commit()
        session.refresh(user_cart)
        cart_items = session.exec(select(CartItem).where(CartItem.cart == user_cart)).all()
        
    return cart_items

@carts_router.put("/{username}/{cart_item_id}/update/", status_code=200, response_model=CartItemReadAll)
async def update_cart_items(username: str, cart_item_id: int, req: CartUpdate, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(is_only_user)]):
    if username != current_user.username:
        raise HTTPException(status_code=403, detail="Unauthorized to update other user's cart")
    
    cart_item = session.exec(select(CartItem).join(Cart).where(CartItem.id == cart_item_id and Cart.user == current_user)).one_or_none()
    
    user_cart = session.exec(select(Cart).where(Cart.user == current_user)).one_or_none()
    
    if user_cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    if cart_item is None:
        raise HTTPException(status_code=404, detail="Cart item not found")

    product = session.get(Product, cart_item.product_id)
    
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    cart_item_data = req.model_dump(exclude_unset=True)
    for key, value in cart_item_data.items():
        if key == "quantity" and product.available_quantity < value:
            raise HTTPException(status_code=409, detail="Not enough stock")
        setattr(cart_item, key, value)
    
    cart_item.updated_at = datetime.datetime.now(datetime.UTC)
    user_cart.updated_at = datetime.datetime.now(datetime.UTC)
    
    session.add(user_cart)
    session.add(cart_item)
    session.commit()
    session.refresh(cart_item)
    return cart_item

@carts_router.delete("/{username}/{cart_item_id}/delete/", status_code=204)
async def remove_cart_item(username: str, cart_item_id: int, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(is_only_user)]):
    if current_user.username != username:
        raise HTTPException(status_code=403, detail="Unauthorized to delete other user's cart")
    
    cart_item = session.exec(select(CartItem).join(Cart).where(CartItem.id == cart_item_id and Cart.user == current_user)).one_or_none()

    if cart_item is None:
        raise HTTPException(status_code=404, detail="Cart item not found")

    session.delete(cart_item)
    session.commit()
    return {"message": "Cart item deleted successfully"}
