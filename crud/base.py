from typing import Generic, TypeVar, Any

DBModelType = TypeVar("DBModelType", bound=Any)

class CRUDBase(Generic[DBModelType]):
    def __init__(self, model: DBModelType):
        self.model = model
