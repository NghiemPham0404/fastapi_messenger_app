from pydantic import BaseModel, ConfigDict
from schemas.message_base import MessageOut
from schemas.conversation_people_base import ConversationPeopleBase

class ConversationBase(BaseModel):
    subject: str
    
class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(ConversationBase):
    pass

class ConversationOut(ConversationBase):
    id : int
    model_config = ConfigDict(from_attributes=True)

class ConversationInDB(ConversationBase):
    pass

class ConversationBaseExtend(ConversationBase):
    messages : list[MessageOut]
    participants : list[ConversationPeopleBase]
    pass