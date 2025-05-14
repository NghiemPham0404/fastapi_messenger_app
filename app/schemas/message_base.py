import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class MessageBase(BaseModel):
    content: str = None

class MessageCreate(MessageBase):
    user_id : int
    conversation_id : int

class MessageUpdate(MessageBase):
    pass

class MessageInDB(MessageBase):
    id : Optional[int] = None
    timestamp : datetime.datetime = datetime.datetime.now
    cp_id: int = None

class MessageOut(MessageBase):
    id : Optional[int] = None
    conversation_id : Optional[int] = None 
    user_id : Optional[int] = None 
    name: Optional[str] = None
    avatar: Optional[str] = None 
    content: Optional[str] = None
    timestamp: Optional[datetime.datetime]
    model_config = ConfigDict(from_attributes=True)
    cp_id: int = None