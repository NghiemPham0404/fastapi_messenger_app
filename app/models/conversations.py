from sqlalchemy import Integer, String, Boolean, Column, TEXT
from ..db.database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key = True, index= True)
    subject = Column(String(255), nullable=False)
    avatar = Column(String(255), nullable=True)
    status = Column(Boolean, default=False)