from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from db.models import Order, OrderItem, OrderItemReadWithProduct, OrderRead, User
from services.crud_user import is_only_user
from utils.deps import get_session

orders_router = APIRouter()

@orders_router.get("/{username}/", response_model=Sequence[OrderRead])
async def get_user_orders(username: str, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(is_only_user)]):
    if username != current_user.username:
        raise HTTPException(status_code=403, detail="Unauthorized to view other user's orders")
    
    user_orders = session.exec(select(Order).where(Order.user == current_user)).all()
    
    return user_orders

@orders_router.get("/{username}/{order_id}/", response_model=Sequence[OrderItemReadWithProduct])
async def get_user_order(username: str, order_id: int, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(is_only_user)]):
    if username != current_user.username:
        raise HTTPException(status_code=403, detail="Unauthorized to view other user's orders")
    
    user_order = session.exec(select(Order).where(Order.id == order_id and Order.user == current_user)).one_or_none()
    
    if user_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    user_order_items = session.exec(select(OrderItem).where(OrderItem.order == user_order)).all()
    
    if len(user_order_items) == 0:
        raise HTTPException(status_code=404, detail="Order is empty")

    return user_order_items

