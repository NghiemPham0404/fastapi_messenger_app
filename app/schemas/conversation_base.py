from typing import Optional
from pydantic import BaseModel, ConfigDict
from .message_base import MessageOut
from .conversation_people_base import ConversationPeopleBase

class ConversationBase(BaseModel):
    subject: str
    
class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(ConversationBase):
    avatar : str
    status : int
    pass

class ConversationOut(ConversationBase):
    id : int
    status : int
    avatar : Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class ConversationInDB(ConversationBase):
    status : Optional[int] = 0
    avatar : Optional[str] = None
    pass

class ConversationBaseExtend(ConversationBase):
    avatar : str
    status : Optional[int] = 0
    messages : list[MessageOut]
    participants : list[ConversationPeopleBase]
    pass