from db.models import User
from crud.base import CRUDBase
from schemas.user import UserCreate

class CRUDUser(CRUDBase[User, UserCreate]):
    pass

user = CRUDUser(User)
