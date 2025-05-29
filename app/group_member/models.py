from typing import Optional
from pydantic import BaseModel, ConfigDict

class GroupMemberBase(BaseModel):
    user_id: int
    group_id: int

class GroupMemberCreate(GroupMemberBase):
    is_host : Optional[bool] = False
    pass

class GroupMemberUpdate(GroupMemberBase):
    is_host : Optional[bool]
    is_sub_host : Optional[bool]
    status : Optional[int]
    pass

class GroupMemberDelete(GroupMemberBase):
    pass

class Member(BaseModel):
    id : int
    name : str
    avatar : Optional[str]
    model_config = ConfigDict(from_attributes=True)

class GroupMemberOut(GroupMemberBase):
    id : int
    is_host : bool
    is_sub_host : bool
    status : int
    member : Member
    model_config = ConfigDict(from_attributes=True)

class GroupMemberInDB(GroupMemberBase):
    is_host : Optional[bool] = False
    is_sub_host : Optional[bool] = False
    status : Optional[int] = 1
    pass