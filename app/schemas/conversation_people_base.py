from pydantic import BaseModel, ConfigDict

class ConversationPeopleBase(BaseModel):
    user_id: int
    conversation_id: int

class ConversationPeopleCreate(ConversationPeopleBase):
    pass

class ConversationPeopleDelete(ConversationPeopleBase):
    pass

class ConversationPeopleOut(ConversationPeopleBase):
    id : int
    model_config = ConfigDict(from_attributes=True)

class ConversationPeopleInDB(ConversationPeopleBase):
    pass