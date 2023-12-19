from pydantic import BaseModel, Field, NonNegativeInt

class CartBase(BaseModel):
    quantity: NonNegativeInt = Field(gt=0)
    
class CartCreate(CartBase):
    pass

class CartUpdate(CartBase):
    pass
