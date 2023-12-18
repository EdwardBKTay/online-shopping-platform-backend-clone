from pydantic import BaseModel, Field
from typing import Optional

class ProductBase(BaseModel):
    name: str
    description: str
    price: float = Field(default=0, ge=0)
    quantity: int = Field(default=0, ge=0)

class ProductCreate(ProductBase):
    pass

# For reference: https://sqlmodel.tiangolo.com/tutorial/fastapi/update/
class ProductUpdate(ProductCreate):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)
    quantity: Optional[int] = Field(default=None, ge=0)
