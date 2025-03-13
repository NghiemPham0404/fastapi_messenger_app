from typing import Optional
from pydantic import BaseModel, ConfigDict
from schemas.conversation_base import ConversationBaseExtend

class UserBase(BaseModel):
    name : Optional[str] = None
    email : Optional[str] = None

class UserCreate(UserBase):
    email : str
    password : str

class UserUpdate(UserBase):
    password :  Optional[str] = None
    avatar : Optional[str] = None

class UserOut(UserBase):
    id: int
    avatar : Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class UserInDB(UserBase):
    hashed_password :  Optional[str] = None
    avatar : Optional[str] = None