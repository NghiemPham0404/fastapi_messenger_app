import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class FCMTokenBase(BaseModel):
    token : str
    user_id : int

class FCMTokenIn(FCMTokenBase):
    updated_at : Optional[datetime.datetime] = datetime.datetime.now(datetime.timezone.utc)

class FCMOut(FCMTokenBase):
    id : int
    updated_at : datetime.datetime
    model_config = ConfigDict(from_attributes=True) 

class FCMInDB(FCMTokenBase):
    token : str
    user_id : int
    updated_at : Optional[datetime.datetime] = datetime.datetime.now(datetime.timezone.utc)