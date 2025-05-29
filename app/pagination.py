from math import ceil
from typing import Generic, List, TypeVar
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")

class Page(BaseModel, Generic[T]):
    items : List[T]
    page  : int
    total_results : int
    total_pages : int
    model_config = ConfigDict(from_attributes=True)
    

