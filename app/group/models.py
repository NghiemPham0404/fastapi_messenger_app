from typing import Optional
from pydantic import BaseModel, ConfigDict

class GroupBase(BaseModel):
    subject: str
    
class GroupCreate(GroupBase):
    pass

class GroupUpdate(GroupBase):
    avatar : Optional[str] = None
    is_public : Optional[bool] = False
    is_member_mute : Optional[bool] = False

class GroupOut(BaseModel):
    id : int
    subject: str
    avatar : Optional[str] = None
    is_public : bool
    is_member_mute : bool
    model_config = ConfigDict(from_attributes=True)

class GroupInDB(GroupBase):
    avatar : Optional[str] = None
    is_public : Optional[bool] = False
    is_member_mute : Optional[bool] = False