from typing import Optional
from pydantic import BaseModel, ConfigDict

class ContactBase(BaseModel):
    pass

class ContactCreate(ContactBase):
    user_id : int
    contact_user_id : int
    status : int

class ContactUpdate(ContactBase):    
    action : str

class OtherContactUser(BaseModel):
    id : int
    name : str
    avatar : str
    model_config = ConfigDict(from_attributes=True)

class ContactOut(ContactBase):
    id : int
    user_id : int
    contact_user_id : int
    status : int
    other_user : Optional[OtherContactUser] = None
    model_config = ConfigDict(from_attributes=True)

class ContactInDB(ContactCreate):
    user_id : int
    status : Optional[int] = 0
