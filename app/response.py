from pydantic import BaseModel, ConfigDict
from typing import Generic, List, TypeVar

T = TypeVar("T")

class Response(BaseModel):
    success : bool = True
    model_config = ConfigDict(from_attributes=True)

class ListResponse(Response, Generic[T]):
    page : int 
    results: List[T] = []
    total_pages : int 
    total_results: int

class MessageResponse(Response):
    message : str

class ObjectResponse(Response, Generic[T]):
    result : T

