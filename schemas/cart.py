from schemas.product import ProductAddToCart
from pydantic import BaseModel
    
class CartCreate(ProductAddToCart):
    pass

class CartUpdate(ProductAddToCart):
    pass
