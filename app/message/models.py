import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from ..user.models import UserOut

class MessageBase(BaseModel):
    user_id : int
    content : Optional[str] = None
    timestamp : Optional[datetime.datetime] = datetime.datetime.now(datetime.timezone.utc)
    file : Optional[str] = None
    images : Optional[list[str]] = None

class DirectMessageCreate(MessageBase):
    receiver_id : int


class GroupMessageCreate(MessageBase):
    group_id : int

class MessageUpdate(BaseModel):
    content : str
    pass

class MessageSender(BaseModel):
    id : int
    name: str = None
    avatar: Optional[str] = None 
    model_config = ConfigDict(from_attributes=True)

class MessageOut(MessageBase):
    # fixed attributes
    id : str
    user_id : int

    # optional attributes
    receiver_id : Optional[int] = None
    group_id : Optional[int] = None

    content : Optional[str] = None
    timestamp : Optional[datetime.datetime] = datetime.datetime.now(datetime.timezone.utc)
    file : Optional[str] = None
    images : Optional[list[str]] = None 

    sender : MessageSender

    model_config = ConfigDict(from_attributes=True)