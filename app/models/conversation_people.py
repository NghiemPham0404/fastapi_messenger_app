from sqlalchemy import Integer, String, Boolean, Column
from db.database import Base

class ConversationPeople(Base):
    __tablename__ = 'conversation_people'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    conversation_id = Column(Integer)