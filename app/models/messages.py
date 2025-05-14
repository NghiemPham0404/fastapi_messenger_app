import datetime
from sqlalchemy import Integer, String, Boolean, Column, DateTime, TEXT, ForeignKey
from ..db.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key = True, index= True)
    content = Column(TEXT)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    cp_id = Column(Integer, ForeignKey("conversation_people.id"))