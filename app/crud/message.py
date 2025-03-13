
import datetime
from models.messages import Message
from sqlalchemy.sql import text
from models.conversation_people import ConversationPeople
from models.users import User 
from sqlalchemy.orm import Session
from crud.base import CRUDRepository

class MessageRepository(CRUDRepository):
    pass
    
crud = MessageRepository(Message)

