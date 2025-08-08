from sqlalchemy import ForeignKey, Integer, String, Boolean, Column, TEXT, DateTime
from ..database import Base

class FCMToken(Base):
    __tablename__ = "fcm_tokens"

    id = Column(Integer, primary_key = True, index= True)
    token = Column(String(255))
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"))
    updated_at = Column(DateTime(timezone=True))
