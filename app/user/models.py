from typing import Optional
from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    name : Optional[str] = None
    email : Optional[str] = None

class UserCreate(UserBase):
    email : str
    password : str

class UserUpdate(UserBase):
    password :  Optional[str] = None
    avatar : Optional[str] = None

class UserOut(BaseModel):
    id: int
    name : str
    email : str
    avatar : Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class Relationship(BaseModel):
    contact_id : Optional[int] = None
    contact_status : int = -1
    is_sent_request : bool = False
    model_config = ConfigDict(from_attributes=True)

class UserOutExtend(UserOut):
   relationship : Relationship
   model_config = ConfigDict(from_attributes=True)


class UserInDB(UserBase):
    hashed_password :  Optional[str] = None
    avatar : Optional[str] = None

