from typing import Optional
from pydantic import BaseModel, ConfigDict

class ContactBase(BaseModel):
    user_id : int
    contact_user_id : int

class ContactCreate(ContactBase):
    pass

class ContactUpdate(ContactBase):
    status : int
    pass

class ContactOut(ContactBase):
    id : int
    status : int
    model_config = ConfigDict(from_attributes=True)

class ContactInDB(ContactCreate):
    id : Optional[int] = None
    status : Optional[int] = 0

