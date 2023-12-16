from db.models import Item
from sqlmodel import Session, select
from fastapi import HTTPException
from typing import Sequence


class CRUDItem:
    def __init__(self, model: Item):
        self.model = model
        
    def get(self, db: Session, item_id: int) -> Item:
        stmt = select(Item).where(Item.id == item_id)
        result = db.exec(stmt).one_or_none()
        
        if result is None:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return result
