import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class Sender(BaseModel):
    id : int
    name : str
    avatar : str

    model_config = ConfigDict(from_attributes=True)

class ConversationOut(BaseModel):
    id : str

    display_name : Optional[str] =""
    display_avatar : Optional[str] =""

    user_id : int
    group_id : Optional[int] = None
    receiver_id : Optional[int] = None 

    content : Optional[str] = None
    timestamp : datetime.datetime

    sender : Sender

    model_config = ConfigDict(from_attributes=True)


