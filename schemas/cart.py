from pydantic import BaseModel, Field

class CartBase(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    
class CartCreate(CartBase):
    pass

class CartUpdate(BaseModel):
    quantity: int = Field(gt=0)
