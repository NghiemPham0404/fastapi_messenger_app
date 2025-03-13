import datetime
from sqlalchemy import Integer, String, Boolean, Column, DateTime, TEXT
from db.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key = True, index= True)
    message = Column(TEXT)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    cp_id = Column(Integer)